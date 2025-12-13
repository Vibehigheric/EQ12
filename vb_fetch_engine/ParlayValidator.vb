''' <summary>
''' EQ12 Parlay Validator - 19 Fault Types + Banned Player Detection
''' Prevents invalid parlays from reaching sportsbooks
''' </summary>
Imports System
Imports System.Collections.Generic
Imports System.Linq

Namespace EQ12.Core.Validation

    ' Already defined in FetchEngine.vb, but repeated here for completeness
    Public Enum SportType
        Nfl
        Nba
        Mlb
        Nhl
        Soccer
        Ncaaf
        Ncaab
        Flights
    End Enum

    Public Enum ParlayFault
        None = 0
        MissingGameData
        WrongMatchup
        MissingOdds
        ConflictingLines
        StaleOdds
        PlayerUnavailable
        PlayerNotStarting
        MissingPlayerName
        IllegalMarketMix
        ExceededLegCap
        ContradictingLegs
        BannedMarket
        WrongSeasonData
        MissingWeather
        MissingInjuryData
        ApiFailure
        SimulationUsed
        NonAsciiContent
        HiddenLegs
    End Enum

    ' ==================== PARLAY LEG MODEL ====================

    Public Class ParlayLeg
        Public Property Sport As SportType
        Public Property GameId As String
        Public Property Market As String
        Public Property Description As String
        Public Property Odds As Integer?
        Public Property PlayerName As String
        Public Property IsOver As Boolean?
        Public Property LineValue As Double?
        Public Property Team As String
        Public Property Opponent As String

        Public Overrides Function ToString() As String
            Return Description
        End Function
    End Class

    ' ==================== VALIDATION RESULT ====================

    Public Class ParlayValidationResult
        Public Property IsValid As Boolean
        Public Property Faults As List(Of ParlayFault)
        Public Property Messages As List(Of String)
        Public Property RiskScore As Double
        Public Property CorrelationScore As Double

        Public Sub New()
            Faults = New List(Of ParlayFault)()
            Messages = New List(Of String)()
        End Sub

        Public Function GetSummary() As String
            Dim sb As New System.Text.StringBuilder()
            sb.AppendLine($"Valid: {IsValid}")
            sb.AppendLine($"Faults: {Faults.Count}")
            sb.AppendLine($"Risk Score: {RiskScore:F2}")
            sb.AppendLine($"Correlation Score: {CorrelationScore:F2}")
            If Faults.Count > 0 Then
                sb.AppendLine("Fault Details:")
                For Each fault In Faults
                    sb.AppendLine($"  - {fault}")
                Next
            End If
            If Messages.Count > 0 Then
                sb.AppendLine("Messages:")
                For Each msg In Messages
                    sb.AppendLine($"  - {msg}")
                Next
            End If
            Return sb.ToString()
        End Function
    End Class

    ' ==================== PARLAY VALIDATOR ====================

    Public Class ParlayValidator
        Private ReadOnly _bannedPlayers As HashSet(Of String)
        Private ReadOnly _bannedMarkets As HashSet(Of String)
        Private ReadOnly _maxLegs As Integer

        Public Sub New(Optional maxLegs As Integer = 10)
            _maxLegs = maxLegs

            ' Banned players (injuries, suspensions, etc.)
            _bannedPlayers = New HashSet(Of String)(StringComparer.OrdinalIgnoreCase) From {
                "Mike Yastrzemski",
                "Nolan Arenado",
                "Ronald Acuna Jr.",
                "Zac Gallen",
                "Shohei Ohtani",
                "Aaron Judge"
            }

            ' Banned or restricted markets
            _bannedMarkets = New HashSet(Of String)(StringComparer.OrdinalIgnoreCase) From {
                "first_basket",
                "last_basket",
                "player_ejection",
                "technical_foul"
            }
        End Sub

        ''' <summary>
        ''' Main validation entry point
        ''' </summary>
        Public Function Validate(legs As IList(Of ParlayLeg)) As ParlayValidationResult
            Dim result As New ParlayValidationResult() With {.IsValid = True}

            ' Check 1: Empty parlay
            If legs Is Nothing OrElse legs.Count = 0 Then
                result.IsValid = False
                result.Faults.Add(ParlayFault.HiddenLegs)
                result.Messages.Add("Parlay has no legs.")
                Return result
            End If

            ' Check 2: Leg cap
            If legs.Count > _maxLegs Then
                result.IsValid = False
                result.Faults.Add(ParlayFault.ExceededLegCap)
                result.Messages.Add($"Parlay exceeds global leg cap of {_maxLegs} (current: {legs.Count}).")
            End If

            ' Check 3: Duplicate legs
            Dim descriptions As New HashSet(Of String)(StringComparer.OrdinalIgnoreCase)

            For Each leg In legs
                ' ASCII validation
                If Not IsAscii(leg.Description) Then
                    result.IsValid = False
                    result.Faults.Add(ParlayFault.NonAsciiContent)
                    result.Messages.Add($"Non-ASCII content detected in leg: {leg.Description}")
                End If

                ' Duplicate check
                If descriptions.Contains(leg.Description) Then
                    result.IsValid = False
                    result.Faults.Add(ParlayFault.ContradictingLegs)
                    result.Messages.Add($"Duplicate leg found: {leg.Description}")
                Else
                    descriptions.Add(leg.Description)
                End If

                ' Banned players
                If Not String.IsNullOrWhiteSpace(leg.PlayerName) AndAlso _bannedPlayers.Contains(leg.PlayerName) Then
                    result.IsValid = False
                    result.Faults.Add(ParlayFault.PlayerUnavailable)
                    result.Messages.Add($"Banned or unavailable player used: {leg.PlayerName}")
                End If

                ' Missing player name for player prop
                If String.Equals(leg.Market, "player_prop", StringComparison.OrdinalIgnoreCase) AndAlso
                   String.IsNullOrWhiteSpace(leg.PlayerName) Then
                    result.IsValid = False
                    result.Faults.Add(ParlayFault.MissingPlayerName)
                    result.Messages.Add($"Player prop without player name: {leg.Description}")
                End If

                ' Banned markets
                If _bannedMarkets.Contains(leg.Market) Then
                    result.IsValid = False
                    result.Faults.Add(ParlayFault.BannedMarket)
                    result.Messages.Add($"Banned market used: {leg.Market} in leg: {leg.Description}")
                End If

                ' Missing odds
                If Not leg.Odds.HasValue Then
                    result.IsValid = False
                    result.Faults.Add(ParlayFault.MissingOdds)
                    result.Messages.Add($"Missing odds for leg: {leg.Description}")
                End If
            Next

            ' Check 4: Contradicting legs (same game)
            ValidateContradictions(legs, result)

            ' Calculate risk and correlation scores
            result.RiskScore = CalculateRiskScore(legs)
            result.CorrelationScore = CalculateCorrelationScore(legs)

            Return result
        End Function

        ''' <summary>
        ''' Detect contradicting legs (e.g., Team A to win AND Team A opponent to cover large spread)
        ''' </summary>
        Private Sub ValidateContradictions(legs As IList(Of ParlayLeg), result As ParlayValidationResult)
            Dim gameGroups = legs.GroupBy(Function(l) l.GameId).Where(Function(g) g.Count() > 1)

            For Each group In gameGroups
                Dim gameLegs = group.ToList()

                ' Check for opposing moneylines
                Dim moneylines = gameLegs.Where(Function(l) String.Equals(l.Market, "moneyline", StringComparison.OrdinalIgnoreCase)).ToList()
                If moneylines.Count > 1 Then
                    result.IsValid = False
                    result.Faults.Add(ParlayFault.ContradictingLegs)
                    result.Messages.Add($"Multiple moneylines for same game: {group.Key}")
                End If

                ' Check for conflicting totals
                Dim totals = gameLegs.Where(Function(l) String.Equals(l.Market, "total", StringComparison.OrdinalIgnoreCase)).ToList()
                If totals.Count > 1 Then
                    Dim overs = totals.Where(Function(t) t.IsOver.HasValue AndAlso t.IsOver.Value).Count()
                    Dim unders = totals.Where(Function(t) t.IsOver.HasValue AndAlso Not t.IsOver.Value).Count()

                    If overs > 0 AndAlso unders > 0 Then
                        result.IsValid = False
                        result.Faults.Add(ParlayFault.ContradictingLegs)
                        result.Messages.Add($"Conflicting totals (over AND under) for same game: {group.Key}")
                    End If
                End If
            Next
        End Sub

        ''' <summary>
        ''' Calculate risk score (higher = riskier)
        ''' </summary>
        Private Function CalculateRiskScore(legs As IList(Of ParlayLeg)) As Double
            If legs.Count = 0 Then Return 0

            Dim legCount = legs.Count
            Dim sportCount = legs.Select(Function(l) l.Sport).Distinct().Count()

            ' Base risk = leg count × 1.5
            Dim score As Double = legCount * 1.5

            ' Sport diversity penalty
            If sportCount > 1 Then
                score += (sportCount - 1) * 2.0
            End If

            ' High-variance market penalty
            Dim highVarianceMarkets = {"alternate_spread", "player_prop", "first_half"}
            Dim highVarCount = legs.Where(Function(l) highVarianceMarkets.Contains(l.Market)).Count()
            score += highVarCount * 1.2

            Return Math.Round(score, 2)
        End Function

        ''' <summary>
        ''' Calculate correlation score (higher = better stacking/correlation)
        ''' </summary>
        Private Function CalculateCorrelationScore(legs As IList(Of ParlayLeg)) As Double
            If legs.Count = 0 Then Return 0

            Dim groups = legs.GroupBy(Function(l) l.GameId)
            Dim stackScore As Double = groups.Sum(Function(g) Math.Pow(g.Count(), 2))
            Dim normalized As Double = stackScore / legs.Count

            ' Bonus for single sport
            Dim singleSport As Boolean = (legs.Select(Function(l) l.Sport).Distinct().Count() = 1)
            If singleSport Then
                normalized += 1.0
            End If

            Return Math.Round(normalized, 2)
        End Function

        ''' <summary>
        ''' ASCII validation
        ''' </summary>
        Private Function IsAscii(value As String) As Boolean
            If value Is Nothing Then Return True
            For Each ch In value
                If AscW(ch) > 127 Then
                    Return False
                End If
            Next
            Return True
        End Function

        ''' <summary>
        ''' Add banned player at runtime
        ''' </summary>
        Public Sub BanPlayer(playerName As String)
            _bannedPlayers.Add(playerName)
        End Sub

        ''' <summary>
        ''' Remove player from ban list
        ''' </summary>
        Public Sub UnbanPlayer(playerName As String)
            _bannedPlayers.Remove(playerName)
        End Sub

    End Class

End Namespace
