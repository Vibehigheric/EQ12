' EQ12 Sports Betting Terminal - Browser Automation Module
' Comprehensive browser automation for scraping odds and placing bets across multiple sportsbooks

Imports OpenQA.Selenium
Imports OpenQA.Selenium.Chrome
Imports OpenQA.Selenium.Firefox
Imports OpenQA.Selenium.Edge
Imports OpenQA.Selenium.Support.UI
Imports System.Threading
Imports System.Threading.Tasks
Imports System.Collections.Generic
Imports System.IO
Imports Newtonsoft.Json

Public Class BrowserModule

    Private drivers As New Dictionary(Of String, IWebDriver)
    Private driverOptions As New Dictionary(Of String, Object)
    Private logger As Action(Of String, String)

    ' Configuration
    Private Const DefaultTimeout As Integer = 30
    Private Const ImplicitWait As Integer = 10
    Private Const PageLoadTimeout As Integer = 60

    ' Supported sportsbooks
    Private ReadOnly supportedBooks As New List(Of String) From {
        "draftkings", "fanduel", "betmgm", "caesars", "pointsbet", "barstool"
    }

    ' Scraping statistics
    Private scrapingStats As New Dictionary(Of String, Integer)

    Public Event BrowserLaunched(browser As String, sportsbook As String, success As Boolean)
    Public Event OddsScraped(sportsbook As String, sport As String, gameCount As Integer, success As Boolean)
    Public Event BetPlaced(sportsbook As String, betDetails As String, success As Boolean)
    Public Event BrowserError(browser As String, errorMessage As String)

    Public Sub New()
        InitializeBrowserModule()

        ' Set up logging
        logger = Sub(message As String, level As String)
                     Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] [{level}] BrowserModule: {message}")
                 End Sub

        logger("Browser Module initialized", "INFO")
    End Sub

    Private Sub InitializeBrowserModule()
        Try
            ' Initialize scraping statistics
            For Each book In supportedBooks
                scrapingStats(book) = 0
            Next

            ' Set up driver options
            SetupDriverOptions()

        Catch ex As Exception
            logger($"Error initializing browser module: {ex.Message}", "ERROR")
            Throw
        End Try
    End Sub

    Private Sub SetupDriverOptions()
        Try
            ' Chrome options
            Dim chromeOptions As New ChromeOptions()
            chromeOptions.AddArgument("--no-sandbox")
            chromeOptions.AddArgument("--disable-dev-shm-usage")
            chromeOptions.AddArgument("--disable-blink-features=AutomationControlled")
            chromeOptions.AddExcludedArgument("enable-automation")
            chromeOptions.AddAdditionalCapability("useAutomationExtension", False)
            chromeOptions.AddUserProfilePreference("profile.default_content_setting_values.notifications", 2)

            ' Add extensions if available
            Dim extensionPath = "C:\EQ12\configs\chrome_extensions"
            If Directory.Exists(extensionPath) Then
                Dim extensions = Directory.GetFiles(extensionPath, "*.crx")
                For Each ext In extensions
                    chromeOptions.AddExtension(ext)
                Next
            End If

            driverOptions("chrome") = chromeOptions

            ' Firefox options
            Dim firefoxOptions As New FirefoxOptions()
            firefoxOptions.AddArgument("-private")
            firefoxOptions.SetPreference("dom.webnotifications.enabled", False)
            firefoxOptions.SetPreference("media.navigator.enabled", False)

            driverOptions("firefox") = firefoxOptions

            ' Edge options
            Dim edgeOptions As New EdgeOptions()
            edgeOptions.AddArgument("--no-sandbox")
            edgeOptions.AddArgument("--disable-dev-shm-usage")

            driverOptions("edge") = edgeOptions

            logger("Driver options configured for all browsers", "SUCCESS")

        Catch ex As Exception
            logger($"Error setting up driver options: {ex.Message}", "ERROR")
        End Try
    End Sub

    Public Async Function LaunchBrowser(browserType As String, sportsbook As String) As Task(Of Boolean)
        Try
            Dim driverKey = $"{browserType}_{sportsbook}"

            ' Close existing driver if present
            If drivers.ContainsKey(driverKey) Then
                CloseBrowser(driverKey)
            End If

            Dim driver As IWebDriver = Nothing

            Select Case browserType.ToLower()
                Case "chrome"
                    Dim service As New ChromeDriverService(ChromeDriverService.CreateDefaultService().DriverServicePath)
                    service.HideCommandPromptWindow = True
                    driver = New ChromeDriver(service, CType(driverOptions("chrome"), ChromeOptions))

                Case "firefox"
                    Dim service As New FirefoxDriverService(GeckoDriverService.CreateDefaultService().DriverServicePath)
                    service.HideCommandPromptWindow = True
                    driver = New FirefoxDriver(service, CType(driverOptions("firefox"), FirefoxOptions))

                Case "edge"
                    Dim service As New EdgeDriverService(EdgeDriverService.CreateDefaultService().DriverServicePath)
                    service.HideCommandPromptWindow = True
                    driver = New EdgeDriver(service, CType(driverOptions("edge"), EdgeOptions))

                Case Else
                    RaiseEvent BrowserError(browserType, $"Unsupported browser type: {browserType}")
                    Return False
            End Select

            If driver Is Nothing Then
                RaiseEvent BrowserError(browserType, "Failed to create driver instance")
                Return False
            End If

            ' Configure driver timeouts
            driver.Manage().Timeouts().ImplicitWait = TimeSpan.FromSeconds(ImplicitWait)
            driver.Manage().Timeouts().PageLoad = TimeSpan.FromSeconds(PageLoadTimeout)

            ' Maximize window
            driver.Manage().Window.Maximize()

            ' Navigate to sportsbook
            Await NavigateToSportsbook(driver, sportsbook)

            ' Store driver
            drivers(driverKey) = driver

            RaiseEvent BrowserLaunched(browserType, sportsbook, True)
            logger($"Browser launched: {browserType} -> {sportsbook}", "SUCCESS")

            Return True

        Catch ex As Exception
            RaiseEvent BrowserError(browserType, ex.Message)
            logger($"Error launching browser {browserType} for {sportsbook}: {ex.Message}", "ERROR")
            Return False
        End Try
    End Function

    Private Async Function NavigateToSportsbook(driver As IWebDriver, sportsbook As String) As Task
        Try
            Dim url As String = ""

            Select Case sportsbook.ToLower()
                Case "draftkings"
                    url = "https://sportsbook.draftkings.com/"
                Case "fanduel"
                    url = "https://sportsbook.fanduel.com/"
                Case "betmgm"
                    url = "https://sports.betmgm.com/"
                Case "caesars"
                    url = "https://www.caesars.com/sportsbook/"
                Case "pointsbet"
                    url = "https://pointsbet.com/"
                Case "barstool"
                    url = "https://www.barstoolsportsbook.com/"
                Case Else
                    Throw New ArgumentException($"Unsupported sportsbook: {sportsbook}")
            End Select

            driver.Navigate().GoToUrl(url)

            ' Wait for page to load
            Await Task.Delay(3000)

            ' Handle any popups or age verification
            Await HandleInitialPopups(driver, sportsbook)

        Catch ex As Exception
            logger($"Error navigating to {sportsbook}: {ex.Message}", "ERROR")
            Throw
        End Try
    End Function

    Private Async Function HandleInitialPopups(driver As IWebDriver, sportsbook As String) As Task
        Try
            Await Task.Delay(2000)

            Select Case sportsbook.ToLower()
                Case "draftkings"
                    ' Handle location popup
                    Try
                        Dim locationButton = driver.FindElement(By.XPath("//button[contains(text(), 'Allow') or contains(@aria-label, 'location')]"))
                        locationButton?.Click()
                        Await Task.Delay(1000)
                    Catch
                        ' Ignore if not found
                    End Try

                Case "fanduel"
                    ' Handle age verification
                    Try
                        Dim ageButton = driver.FindElement(By.XPath("//button[contains(text(), '21+') or contains(text(), 'Enter')]"))
                        ageButton?.Click()
                        Await Task.Delay(1000)
                    Catch
                        ' Ignore if not found
                    End Try

                Case "betmgm"
                    ' Handle welcome popup
                    Try
                        Dim closeButton = driver.FindElement(By.XPath("//button[contains(@class, 'close') or contains(@aria-label, 'close')]"))
                        closeButton?.Click()
                        Await Task.Delay(1000)
                    Catch
                        ' Ignore if not found
                    End Try
            End Select

        Catch ex As Exception
            logger($"Error handling popups for {sportsbook}: {ex.Message}", "WARNING")
            ' Don't throw - popups are not critical
        End Try
    End Function

    Public Async Function ScrapeOdds(sportsbook As String, sport As String) As Task(Of List(Of Dictionary(Of String, Object)))
        Try
            Dim driverKey = $"chrome_{sportsbook}"

            If Not drivers.ContainsKey(driverKey) Then
                Await LaunchBrowser("chrome", sportsbook)
            End If

            If Not drivers.ContainsKey(driverKey) Then
                RaiseEvent OddsScraped(sportsbook, sport, 0, False)
                Return New List(Of Dictionary(Of String, Object))
            End If

            Dim driver = drivers(driverKey)
            Dim oddsData As New List(Of Dictionary(Of String, Object))

            Select Case sportsbook.ToLower()
                Case "draftkings"
                    oddsData = Await ScrapeDraftKingsOdds(driver, sport)
                Case "fanduel"
                    oddsData = Await ScrapeFanDuelOdds(driver, sport)
                Case "betmgm"
                    oddsData = Await ScrapeBetMGMOdds(driver, sport)
                Case "caesars"
                    oddsData = Await ScrapeCaesarsOdds(driver, sport)
                Case Else
                    logger($"Scraping not implemented for {sportsbook}", "WARNING")
            End Select

            scrapingStats(sportsbook) += oddsData.Count

            RaiseEvent OddsScraped(sportsbook, sport, oddsData.Count, True)
            logger($"Scraped {oddsData.Count} odds from {sportsbook} for {sport}", "SUCCESS")

            Return oddsData

        Catch ex As Exception
            RaiseEvent OddsScraped(sportsbook, sport, 0, False)
            logger($"Error scraping odds from {sportsbook}: {ex.Message}", "ERROR")
            Return New List(Of Dictionary(Of String, Object))
        End Try
    End Function

    Private Async Function ScrapeDraftKingsOdds(driver As IWebDriver, sport As String) As Task(Of List(Of Dictionary(Of String, Object)))
        Try
            Dim oddsData As New List(Of Dictionary(Of String, Object))

            ' Navigate to sport section
            Dim sportUrl = GetDraftKingsSportUrl(sport)
            driver.Navigate().GoToUrl(sportUrl)
            Await Task.Delay(5000)

            ' Find game elements
            Dim gameElements = driver.FindElements(By.CssSelector(".sportsbook-table__body tr"))

            For Each gameElement In gameElements.Take(10) ' Limit to first 10 games
                Try
                    Dim teams = gameElement.FindElements(By.CssSelector(".event-cell__name-text"))
                    If teams.Count >= 2 Then
                        Dim homeTeam = teams(1).Text.Trim()
                        Dim awayTeam = teams(0).Text.Trim()

                        ' Get moneyline odds
                        Dim oddsElements = gameElement.FindElements(By.CssSelector(".sportsbook-odds"))
                        If oddsElements.Count >= 2 Then
                            Dim awayOdds = oddsElements(0).Text.Trim()
                            Dim homeOdds = oddsElements(1).Text.Trim()

                            ' Create odds entry
                            Dim oddsEntry = New Dictionary(Of String, Object) From {
                                {"game_id", $"{awayTeam}_vs_{homeTeam}_{DateTime.Now:yyyyMMdd}"},
                                {"sport", sport},
                                {"home_team", homeTeam},
                                {"away_team", awayTeam},
                                {"commence_time", DateTime.Now.AddHours(2)}, ' Estimate
                                {"sportsbook", "draftkings"},
                                {"market_type", "h2h"},
                                {"outcome_name", homeTeam},
                                {"odds_american", ParseAmericanOdds(homeOdds)},
                                {"odds_decimal", ConvertAmericanToDecimal(ParseAmericanOdds(homeOdds))}
                            }

                            oddsData.Add(oddsEntry)

                            ' Add away team odds
                            Dim awayEntry = New Dictionary(Of String, Object)(oddsEntry)
                            awayEntry("outcome_name") = awayTeam
                            awayEntry("odds_american") = ParseAmericanOdds(awayOdds)
                            awayEntry("odds_decimal") = ConvertAmericanToDecimal(ParseAmericanOdds(awayOdds))

                            oddsData.Add(awayEntry)
                        End If
                    End If

                Catch ex As Exception
                    logger($"Error parsing game element: {ex.Message}", "WARNING")
                End Try
            Next

            Return oddsData

        Catch ex As Exception
            logger($"Error scraping DraftKings odds: {ex.Message}", "ERROR")
            Return New List(Of Dictionary(Of String, Object))
        End Try
    End Function

    Private Async Function ScrapeFanDuelOdds(driver As IWebDriver, sport As String) As Task(Of List(Of Dictionary(Of String, Object)))
        Try
            Dim oddsData As New List(Of Dictionary(Of String, Object))

            ' Navigate to sport section
            Dim sportUrl = GetFanDuelSportUrl(sport)
            driver.Navigate().GoToUrl(sportUrl)
            Await Task.Delay(5000)

            ' FanDuel uses different selectors
            Dim gameElements = driver.FindElements(By.CssSelector("[data-test-id='MarketGrid'] tbody tr"))

            For Each gameElement In gameElements.Take(10)
                Try
                    ' Extract team names and odds
                    Dim teamElements = gameElement.FindElements(By.CssSelector("[data-test-id='team-name']"))
                    Dim oddsElements = gameElement.FindElements(By.CssSelector("[data-test-id='odds']"))

                    If teamElements.Count >= 2 AndAlso oddsElements.Count >= 2 Then
                        Dim awayTeam = teamElements(0).Text.Trim()
                        Dim homeTeam = teamElements(1).Text.Trim()
                        Dim awayOdds = oddsElements(0).Text.Trim()
                        Dim homeOdds = oddsElements(1).Text.Trim()

                        ' Create odds entries similar to DraftKings
                        Dim homeEntry = New Dictionary(Of String, Object) From {
                            {"game_id", $"{awayTeam}_vs_{homeTeam}_{DateTime.Now:yyyyMMdd}"},
                            {"sport", sport},
                            {"home_team", homeTeam},
                            {"away_team", awayTeam},
                            {"commence_time", DateTime.Now.AddHours(2)},
                            {"sportsbook", "fanduel"},
                            {"market_type", "h2h"},
                            {"outcome_name", homeTeam},
                            {"odds_american", ParseAmericanOdds(homeOdds)},
                            {"odds_decimal", ConvertAmericanToDecimal(ParseAmericanOdds(homeOdds))}
                        }

                        oddsData.Add(homeEntry)

                        Dim awayEntry = New Dictionary(Of String, Object)(homeEntry)
                        awayEntry("outcome_name") = awayTeam
                        awayEntry("odds_american") = ParseAmericanOdds(awayOdds)
                        awayEntry("odds_decimal") = ConvertAmericanToDecimal(ParseAmericanOdds(awayOdds))

                        oddsData.Add(awayEntry)
                    End If

                Catch ex As Exception
                    logger($"Error parsing FanDuel game element: {ex.Message}", "WARNING")
                End Try
            Next

            Return oddsData

        Catch ex As Exception
            logger($"Error scraping FanDuel odds: {ex.Message}", "ERROR")
            Return New List(Of Dictionary(Of String, Object))
        End Try
    End Function

    Private Async Function ScrapeBetMGMOdds(driver As IWebDriver, sport As String) As Task(Of List(Of Dictionary(Of String, Object)))
        ' Placeholder implementation - would need specific selectors for BetMGM
        Return New List(Of Dictionary(Of String, Object))
    End Function

    Private Async Function ScrapeCaesarsOdds(driver As IWebDriver, sport As String) As Task(Of List(Of Dictionary(Of String, Object)))
        ' Placeholder implementation - would need specific selectors for Caesars
        Return New List(Of Dictionary(Of String, Object))
    End Function

    Private Function GetDraftKingsSportUrl(sport As String) As String
        Select Case sport.ToLower()
            Case "baseball_mlb", "mlb"
                Return "https://sportsbook.draftkings.com/leagues/baseball/mlb"
            Case "american_football_nfl", "nfl"
                Return "https://sportsbook.draftkings.com/leagues/football/nfl"
            Case "basketball_nba", "nba"
                Return "https://sportsbook.draftkings.com/leagues/basketball/nba"
            Case Else
                Return "https://sportsbook.draftkings.com/"
        End Select
    End Function

    Private Function GetFanDuelSportUrl(sport As String) As String
        Select Case sport.ToLower()
            Case "baseball_mlb", "mlb"
                Return "https://sportsbook.fanduel.com/baseball"
            Case "american_football_nfl", "nfl"
                Return "https://sportsbook.fanduel.com/football"
            Case "basketball_nba", "nba"
                Return "https://sportsbook.fanduel.com/basketball"
            Case Else
                Return "https://sportsbook.fanduel.com/"
        End Select
    End Function

    Private Function ParseAmericanOdds(oddsText As String) As Integer
        Try
            ' Remove any non-digit characters except +/-
            Dim cleanOdds = System.Text.RegularExpressions.Regex.Replace(oddsText, "[^+\-\d]", "")

            If String.IsNullOrEmpty(cleanOdds) Then
                Return 100
            End If

            Return Integer.Parse(cleanOdds)

        Catch ex As Exception
            logger($"Error parsing American odds '{oddsText}': {ex.Message}", "WARNING")
            Return 100
        End Try
    End Function

    Private Function ConvertAmericanToDecimal(americanOdds As Integer) As Double
        Try
            If americanOdds > 0 Then
                Return (americanOdds / 100.0) + 1
            Else
                Return (100.0 / Math.Abs(americanOdds)) + 1
            End If

        Catch ex As Exception
            logger($"Error converting American odds {americanOdds}: {ex.Message}", "WARNING")
            Return 2.0
        End Try
    End Function

    Public Async Function PlaceBet(sportsbook As String, betDetails As Dictionary(Of String, Object)) As Task(Of Boolean)
        Try
            ' This would be a complex implementation requiring login handling
            ' and bet slip automation - placeholder for now

            logger($"Bet placement not implemented for {sportsbook}", "WARNING")
            RaiseEvent BetPlaced(sportsbook, JsonConvert.SerializeObject(betDetails), False)

            Return False

        Catch ex As Exception
            logger($"Error placing bet on {sportsbook}: {ex.Message}", "ERROR")
            RaiseEvent BetPlaced(sportsbook, JsonConvert.SerializeObject(betDetails), False)
            Return False
        End Try
    End Function

    Public Sub CloseBrowser(driverKey As String)
        Try
            If drivers.ContainsKey(driverKey) Then
                drivers(driverKey).Quit()
                drivers(driverKey).Dispose()
                drivers.Remove(driverKey)

                logger($"Browser closed: {driverKey}", "INFO")
            End If

        Catch ex As Exception
            logger($"Error closing browser {driverKey}: {ex.Message}", "ERROR")
        End Try
    End Sub

    Public Sub CloseAllBrowsers()
        Try
            Dim keys = drivers.Keys.ToList()

            For Each key In keys
                CloseBrowser(key)
            Next

            logger($"All browsers closed ({keys.Count} instances)", "INFO")

        Catch ex As Exception
            logger($"Error closing all browsers: {ex.Message}", "ERROR")
        End Try
    End Sub

    Public Function GetBrowserStatus() As Dictionary(Of String, Object)
        Try
            Return New Dictionary(Of String, Object) From {
                {"active_browsers", drivers.Count},
                {"browser_instances", drivers.Keys.ToList()},
                {"supported_sportsbooks", supportedBooks},
                {"scraping_stats", scrapingStats},
                {"total_scraped", scrapingStats.Values.Sum()}
            }

        Catch ex As Exception
            logger($"Error getting browser status: {ex.Message}", "ERROR")
            Return New Dictionary(Of String, Object)
        End Try
    End Function

    Public Sub Dispose()
        Try
            CloseAllBrowsers()
            logger("Browser Module disposed", "INFO")

        Catch ex As Exception
            logger($"Error disposing Browser Module: {ex.Message}", "ERROR")
        End Try
    End Sub

End Class
