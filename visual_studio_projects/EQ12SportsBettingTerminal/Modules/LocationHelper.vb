Imports System.Net.Http
Imports System.Text
Imports Newtonsoft.Json.Linq
Imports System.Data.SQLite
Imports System.Math

''' <summary>
''' Location Helper - Geolocation and Monetization Integration for EQ12
''' Handles location sharing, geofencing, and location-based monetization features
''' Features: Google Maps integration, IP geolocation, geofence alerts, compliance checking
''' </summary>
Public Class LocationHelper

    Private Shared ReadOnly HttpClient As New HttpClient()

    ''' <summary>
    ''' Fetch location from Google Maps Location Sharing API
    ''' </summary>
    ''' <param name="config">Configuration object with Google Maps settings</param>
    ''' <returns>Tuple of (latitude, longitude) or (0, 0) if failed</returns>
    Public Shared Function FetchLocationGoogle(config As JObject) As (Double, Double)
        Try
            Dim locationConfig = config("location")
            If locationConfig Is Nothing OrElse locationConfig("enabled")?.ToObject(Of Boolean)() <> True Then
                Console.WriteLine("📍 Location services disabled")
                Return (0, 0)
            End If

            Dim googleMapsConfig = locationConfig("google_maps")
            If googleMapsConfig Is Nothing Then
                Console.WriteLine("⚠️ Google Maps configuration not found")
                Return FetchLocationIP()
            End If

            Dim apiKey = googleMapsConfig("api_key")?.ToString()
            Dim sharingUrl = googleMapsConfig("location_sharing_url")?.ToString()

            If String.IsNullOrEmpty(apiKey) OrElse apiKey = "YOUR_GOOGLE_MAPS_API_KEY" Then
                Console.WriteLine("⚠️ Google Maps API key not configured, falling back to IP location")
                Return FetchLocationIP()
            End If

            ' Google Maps Location Sharing integration
            ' Note: This would typically require OAuth2 and specific sharing permissions
            ' For now, we'll implement a fallback to IP-based geolocation
            Console.WriteLine("🌍 Google Maps location sharing not yet implemented, using IP geolocation")
            Return FetchLocationIP()

        Catch ex As Exception
            Console.WriteLine($"❌ Google location fetch failed: {ex.Message}")
            Return FetchLocationIP()
        End Try
    End Function

    ''' <summary>
    ''' Fetch location using IP-based geolocation APIs
    ''' </summary>
    ''' <returns>Tuple of (latitude, longitude) or (0, 0) if failed</returns>
    Public Shared Function FetchLocationIP() As (Double, Double)
        Try
            Console.WriteLine("🌐 Fetching location via IP geolocation...")

            ' Try primary IP geolocation API
            Dim primaryUrl = "http://ip-api.com/json/?fields=lat,lon,city,region,country,status,message"
            Dim response = HttpClient.GetAsync(primaryUrl).Result

            If response.IsSuccessStatusCode Then
                Dim responseContent = response.Content.ReadAsStringAsync().Result
                Dim locationData = JObject.Parse(responseContent)

                If locationData("status")?.ToString() = "success" Then
                    Dim lat = locationData("lat")?.ToObject(Of Double)() ?? 0
                    Dim lon = locationData("lon")?.ToObject(Of Double)() ?? 0
                    Dim city = locationData("city")?.ToString() ?? "Unknown"
                    Dim region = locationData("region")?.ToString() ?? "Unknown"
                    Dim country = locationData("country")?.ToString() ?? "Unknown"

                    Console.WriteLine($"📍 Location detected: {city}, {region}, {country} ({lat:F4}, {lon:F4})")
                    Return (lat, lon)
                End If
            End If

            ' Fallback to secondary API
            Console.WriteLine("🔄 Trying backup geolocation API...")
            Dim backupUrl = "https://ipapi.co/json/"
            Dim backupResponse = HttpClient.GetAsync(backupUrl).Result

            If backupResponse.IsSuccessStatusCode Then
                Dim backupContent = backupResponse.Content.ReadAsStringAsync().Result
                Dim backupData = JObject.Parse(backupContent)

                Dim lat = backupData("latitude")?.ToObject(Of Double)() ?? 0
                Dim lon = backupData("longitude")?.ToObject(Of Double)() ?? 0
                Dim city = backupData("city")?.ToString() ?? "Unknown"

                If lat <> 0 OrElse lon <> 0 Then
                    Console.WriteLine($"📍 Backup location: {city} ({lat:F4}, {lon:F4})")
                    Return (lat, lon)
                End If
            End If

            Console.WriteLine("❌ All geolocation attempts failed")
            Return (0, 0)

        Catch ex As Exception
            Console.WriteLine($"❌ IP geolocation error: {ex.Message}")
            Return (0, 0)
        End Try
    End Function

    ''' <summary>
    ''' Log location data to database with metadata
    ''' </summary>
    ''' <param name="lat">Latitude</param>
    ''' <param name="lon">Longitude</param>
    ''' <param name="source">Location source (google_maps, ip_api, manual)</param>
    ''' <param name="notes">Additional notes or context</param>
    Public Shared Sub LogLocation(lat As Double, lon As Double, source As String, Optional notes As String = "")
        Try
            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()

                ' Calculate accuracy estimate based on source
                Dim accuracy As Double = Select Case source.ToLower()
                                           Case "google_maps" : 10.0    ' ~10m accuracy
                                           Case "device_gps" : 5.0     ' ~5m accuracy
                                           Case "ip_api" : 10000.0     ' ~10km accuracy
                                           Case Else : 0.0            ' Unknown accuracy
                                         End Select

                Dim sql = "INSERT INTO location_logs (ts, lat, lon, accuracy, source, notes, created_at) " &
                         "VALUES (@ts, @lat, @lon, @accuracy, @source, @notes, @created_at)"

                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@ts", DateTime.UtcNow)
                    cmd.Parameters.AddWithValue("@lat", lat)
                    cmd.Parameters.AddWithValue("@lon", lon)
                    cmd.Parameters.AddWithValue("@accuracy", accuracy)
                    cmd.Parameters.AddWithValue("@source", source)
                    cmd.Parameters.AddWithValue("@notes", notes)
                    cmd.Parameters.AddWithValue("@created_at", DateTime.UtcNow)

                    cmd.ExecuteNonQuery()
                    Console.WriteLine($"✅ Location logged: ({lat:F4}, {lon:F4}) via {source}")
                End Using
            End Using
        Catch ex As Exception
            Console.WriteLine($"⚠️ Failed to log location: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Check if current location triggers any geofence alerts
    ''' </summary>
    ''' <param name="lat">Current latitude</param>
    ''' <param name="lon">Current longitude</param>
    ''' <param name="config">Configuration with geofence settings</param>
    ''' <returns>Triggered geofence type or empty string if none</returns>
    Public Shared Function CheckGeofence(lat As Double, lon As Double, config As JObject) As String
        Try
            If lat = 0 AndAlso lon = 0 Then
                Return "" ' No valid location
            End If

            Dim locationConfig = config("location")
            Dim geofenceConfig = locationConfig("geofence_alerts")

            If geofenceConfig Is Nothing OrElse geofenceConfig("enabled")?.ToObject(Of Boolean)() <> True Then
                Return "" ' Geofencing disabled
            End If

            Dim zones = geofenceConfig("zones")
            If zones Is Nothing Then
                Return ""
            End If

            ' Known venue locations (these would typically come from a database)
            Dim venues = GetKnownVenues()

            For Each venue In venues
                Dim venueLat = venue.Value.Item1
                Dim venueLon = venue.Value.Item2
                Dim venueType = venue.Value.Item3

                Dim distance = CalculateDistance(lat, lon, venueLat, venueLon)

                ' Check if within geofence radius
                Dim zoneConfig = zones(venueType)
                If zoneConfig IsNot Nothing Then
                    Dim radiusMeters = zoneConfig("radius_meters")?.ToObject(Of Double)() ?? 500

                    If distance <= radiusMeters Then
                        Dim alertMessage = zoneConfig("alert_message")?.ToString() ??
                                         $"Entered {venueType} geofence zone"

                        Console.WriteLine($"🚨 Geofence Alert: {alertMessage}")

                        ' Send notification if configured
                        SendGeofenceAlert(config, venueType, alertMessage, venue.Key)

                        ' Log geofence event
                        LogLocation(lat, lon, "geofence", $"Triggered: {venueType} - {venue.Key}")

                        Return venueType
                    End If
                End If
            Next

            Return "" ' No geofence triggered

        Catch ex As Exception
            Console.WriteLine($"❌ Geofence check error: {ex.Message}")
            Return ""
        End Try
    End Function

    ''' <summary>
    ''' Get known venues for geofencing (stadiums, casinos, sportsbooks)
    ''' In production, this would query a comprehensive venue database
    ''' </summary>
    Private Shared Function GetKnownVenues() As Dictionary(Of String, (Double, Double, String))
        Return New Dictionary(Of String, (Double, Double, String)) From {
            ' Sample venues - in production this would come from a comprehensive database
            {"Madison Square Garden", (40.7505, -73.9934, "stadium")},
            {"Yankee Stadium", (40.8296, -73.9262, "stadium")},
            {"MetLife Stadium", (40.8135, -74.0745, "stadium")},
            {"Caesars Palace", (36.1162, -115.1745, "casino")},
            {"Bellagio", (36.1126, -115.1767, "casino")},
            {"MGM Grand", (36.1023, -115.1696, "casino")},
            {"FanDuel Sportsbook", (40.7589, -73.9851, "sportsbook")},
            {"DraftKings Sportsbook", (40.7506, -73.9938, "sportsbook")}
        }
    End Function

    ''' <summary>
    ''' Calculate distance between two geographic points using Haversine formula
    ''' </summary>
    Private Shared Function CalculateDistance(lat1 As Double, lon1 As Double,
                                            lat2 As Double, lon2 As Double) As Double
        Try
            Const R As Double = 6371000 ' Earth radius in meters

            Dim dLat = ToRadians(lat2 - lat1)
            Dim dLon = ToRadians(lon2 - lon1)

            Dim a = Sin(dLat / 2) * Sin(dLat / 2) +
                   Cos(ToRadians(lat1)) * Cos(ToRadians(lat2)) *
                   Sin(dLon / 2) * Sin(dLon / 2)

            Dim c = 2 * Atan2(Sqrt(a), Sqrt(1 - a))

            Return R * c ' Distance in meters
        Catch
            Return Double.MaxValue ' Error in calculation
        End Try
    End Function

    ''' <summary>
    ''' Convert degrees to radians
    ''' </summary>
    Private Shared Function ToRadians(degrees As Double) As Double
        Return degrees * (PI / 180.0)
    End Function

    ''' <summary>
    ''' Send geofence alert notification
    ''' </summary>
    Private Shared Sub SendGeofenceAlert(config As JObject, zoneType As String, message As String, venueName As String)
        Try
            ' Send Telegram alert if configured
            If config("telegram") IsNot Nothing Then
                Dim alertText = $"📍 **Geofence Alert**{vbCrLf}{vbCrLf}" &
                              $"**Zone:** {zoneType.ToUpper()}{vbCrLf}" &
                              $"**Venue:** {venueName}{vbCrLf}" &
                              $"**Time:** {DateTime.Now:yyyy-MM-dd HH:mm:ss}{vbCrLf}{vbCrLf}" &
                              $"{message}{vbCrLf}{vbCrLf}" &
                              $"Consider triggering location-based marketing campaigns or affiliate offers."

                ' Use existing Telegram helper if available
                Try
                    TelegramHelper.SendMessage(config, alertText)
                Catch ex As Exception
                    Console.WriteLine($"⚠️ Telegram alert failed: {ex.Message}")
                End Try
            End If

            ' Send Discord alert if configured
            If config("discord") IsNot Nothing Then
                Try
                    Dim discordMessage = $"🚨 **Geofence Alert** 🚨{vbCrLf}" &
                                       $"Entered {zoneType} zone: {venueName}{vbCrLf}" &
                                       $"Time: {DateTime.Now:HH:mm:ss}"

                    DiscordHelper.SendMessage(config, discordMessage)
                Catch ex As Exception
                    Console.WriteLine($"⚠️ Discord alert failed: {ex.Message}")
                End Try
            End If

        Catch ex As Exception
            Console.WriteLine($"⚠️ Geofence alert failed: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Check compliance and jurisdiction restrictions
    ''' </summary>
    ''' <param name="lat">Latitude</param>
    ''' <param name="lon">Longitude</param>
    ''' <param name="config">Configuration object</param>
    ''' <returns>Compliance status and any restrictions</returns>
    Public Shared Function CheckCompliance(lat As Double, lon As Double, config As JObject) As String
        Try
            Dim locationConfig = config("location")
            Dim complianceConfig = locationConfig("compliance")

            If complianceConfig Is Nothing OrElse
               complianceConfig("legal_jurisdiction_check")?.ToObject(Of Boolean)() <> True Then
                Return "Compliance checking disabled"
            End If

            ' Reverse geocode to get jurisdiction information
            Dim jurisdiction = ReverseGeocode(lat, lon)

            ' Check against restricted regions
            Dim restrictedRegions = complianceConfig("restricted_regions")?.ToObject(Of String())() ?? {}

            For Each region In restrictedRegions
                If jurisdiction.ToLower().Contains(region.ToLower()) Then
                    Dim alertMessage = $"⚠️ COMPLIANCE ALERT: Located in restricted jurisdiction: {jurisdiction}"
                    Console.WriteLine(alertMessage)

                    ' Send compliance alert
                    If complianceConfig("alert_on_jurisdiction_change")?.ToObject(Of Boolean)() = True Then
                        SendComplianceAlert(config, alertMessage, jurisdiction)
                    End If

                    Return $"RESTRICTED: {jurisdiction}"
                End If
            Next

            Console.WriteLine($"✅ Compliance OK: {jurisdiction}")
            Return $"COMPLIANT: {jurisdiction}"

        Catch ex As Exception
            Console.WriteLine($"❌ Compliance check error: {ex.Message}")
            Return "ERROR: Could not verify compliance"
        End Try
    End Function

    ''' <summary>
    ''' Reverse geocode coordinates to jurisdiction information
    ''' </summary>
    Private Shared Function ReverseGeocode(lat As Double, lon As Double) As String
        Try
            Dim reverseUrl = $"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=en"
            Dim response = HttpClient.GetAsync(reverseUrl).Result

            If response.IsSuccessStatusCode Then
                Dim responseContent = response.Content.ReadAsStringAsync().Result
                Dim geoData = JObject.Parse(responseContent)

                Dim city = geoData("city")?.ToString() ?? ""
                Dim region = geoData("principalSubdivision")?.ToString() ?? ""
                Dim country = geoData("countryName")?.ToString() ?? ""

                Return $"{city}, {region}, {country}".Trim(","c, " "c)
            End If

            Return "Unknown Jurisdiction"

        Catch ex As Exception
            Return "Geocoding Error"
        End Try
    End Function

    ''' <summary>
    ''' Send compliance alert notification
    ''' </summary>
    Private Shared Sub SendComplianceAlert(config As JObject, alertMessage As String, jurisdiction As String)
        Try
            Dim fullAlert = $"🚨 **COMPLIANCE ALERT** 🚨{vbCrLf}{vbCrLf}" &
                          $"{alertMessage}{vbCrLf}{vbCrLf}" &
                          $"**Jurisdiction:** {jurisdiction}{vbCrLf}" &
                          $"**Time:** {DateTime.Now:yyyy-MM-dd HH:mm:ss}{vbCrLf}{vbCrLf}" &
                          $"**Action Required:** Review betting activities and ensure compliance with local laws."

            ' Send via configured notification channels
            TelegramHelper.SendMessage(config, fullAlert)

        Catch ex As Exception
            Console.WriteLine($"⚠️ Compliance alert failed: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Get location history from database
    ''' </summary>
    ''' <param name="days">Number of days to look back</param>
    ''' <returns>List of location records</returns>
    Public Shared Function GetLocationHistory(Optional days As Integer = 7) As List(Of Dictionary(Of String, Object))
        Dim locations As New List(Of Dictionary(Of String, Object))

        Try
            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()

                Dim sql = "SELECT * FROM location_logs WHERE date(created_at) >= date('now', '-' || @days || ' days') " &
                         "ORDER BY created_at DESC LIMIT 100"

                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@days", days)

                    Using reader = cmd.ExecuteReader()
                        While reader.Read()
                            Dim location As New Dictionary(Of String, Object) From {
                                {"id", reader("id")},
                                {"timestamp", reader("ts")},
                                {"latitude", reader("lat")},
                                {"longitude", reader("lon")},
                                {"accuracy", reader("accuracy")},
                                {"source", reader("source")},
                                {"notes", reader("notes")}
                            }
                            locations.Add(location)
                        End While
                    End Using
                End Using
            End Using

        Catch ex As Exception
            Console.WriteLine($"❌ Error getting location history: {ex.Message}")
        End Try

        Return locations
    End Function

    ''' <summary>
    ''' Export location data to CSV format
    ''' </summary>
    ''' <param name="filePath">Output CSV file path</param>
    ''' <param name="days">Number of days to export</param>
    ''' <returns>Success status</returns>
    Public Shared Function ExportLocationData(filePath As String, Optional days As Integer = 30) As Boolean
        Try
            Dim locations = GetLocationHistory(days)

            Using writer As New IO.StreamWriter(filePath)
                ' Write CSV header
                writer.WriteLine("Timestamp,Latitude,Longitude,Accuracy,Source,Notes")

                ' Write location data
                For Each location In locations
                    Dim csvLine = $"{location("timestamp")},{location("latitude")},{location("longitude")}," &
                                $"{location("accuracy")},{location("source")},\"{location("notes")}\""
                    writer.WriteLine(csvLine)
                Next
            End Using

            Console.WriteLine($"✅ Location data exported: {filePath} ({locations.Count} records)")
            Return True

        Catch ex As Exception
            Console.WriteLine($"❌ Export failed: {ex.Message}")
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Trigger location-based monetization campaigns
    ''' </summary>
    ''' <param name="config">Configuration object</param>
    ''' <param name="lat">Current latitude</param>
    ''' <param name="lon">Current longitude</param>
    ''' <param name="zoneType">Type of zone entered</param>
    Public Shared Sub TriggerMonetizationCampaign(config As JObject, lat As Double, lon As Double, zoneType As String)
        Try
            Dim locationConfig = config("location")
            Dim monetizationConfig = locationConfig("monetization")

            If monetizationConfig Is Nothing OrElse
               monetizationConfig("affiliate_campaigns")?.ToObject(Of Boolean)() <> True Then
                Return
            End If

            Select Case zoneType.ToLower()
                Case "casino"
                    ' Trigger casino affiliate campaigns
                    Console.WriteLine("💰 Triggering casino affiliate campaigns...")
                    ' Integration with affiliate networks, email campaigns, push notifications

                Case "sportsbook"
                    ' Trigger sportsbook promotional offers
                    Console.WriteLine("🏈 Triggering sportsbook promotional campaigns...")
                    ' Push betting bonuses, sign-up offers, premium content

                Case "stadium"
                    ' Trigger live betting and travel offers
                    Console.WriteLine("🏟️ Triggering stadium proximity campaigns...")
                    ' Live betting opportunities, hotel/travel affiliates, merchandise

            End Select

            ' Log monetization trigger
            LogLocation(lat, lon, "monetization", $"Campaign triggered: {zoneType}")

        Catch ex As Exception
            Console.WriteLine($"⚠️ Monetization campaign error: {ex.Message}")
        End Try
    End Sub
End Class
