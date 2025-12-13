Option Strict On
Option Explicit On

Imports System.Threading.Tasks

Namespace EQ12.Core.ApiClient

    ''' <summary>
    ''' Client for OpenWeatherMap API
    ''' Used for game-day weather conditions (MLB, NFL, outdoor sports)
    ''' </summary>
    Public Class WeatherApiClient
        Inherits ApiClientBase

        Private ReadOnly _apiKey As String

        Public Sub New(Optional apiKey As String = Nothing)
            Dim catalog As New ApiCatalog()
            Dim apiInfo = catalog.FindByName("OpenWeatherMap")
            
            MyBase.New(apiInfo, apiKey)
            
            ' Load API key
            _apiKey = If(apiKey, Environment.GetEnvironmentVariable(apiInfo.EnvironmentVariableName))
            
            If String.IsNullOrWhiteSpace(_apiKey) Then
                Throw New ArgumentException($"API key required for {apiInfo.Name}. Set {apiInfo.EnvironmentVariableName} environment variable.")
            End If
        End Sub

        Public Overrides Async Function TestConnectionAsync() As Task(Of String)
            ' Test with New York coordinates
            Dim result = Await GetCurrentWeatherAsync(40.7128, -74.0060)
            
            Return $"✅ {ApiInfo.Name} - Status: Connected{Environment.NewLine}" &
                   $"Test location: New York{Environment.NewLine}" &
                   result.Substring(0, Math.Min(300, result.Length))
        End Function

        ''' <summary>
        ''' Get current weather for coordinates
        ''' </summary>
        Public Async Function GetCurrentWeatherAsync(latitude As Double, longitude As Double) As Task(Of String)
            Dim url = $"data/2.5/weather?lat={latitude}&lon={longitude}&appid={_apiKey}&units=imperial"
            Return Await GetAsync(url)
        End Function

        ''' <summary>
        ''' Get weather forecast for coordinates
        ''' </summary>
        Public Async Function GetForecastAsync(latitude As Double, longitude As Double) As Task(Of String)
            Dim url = $"data/2.5/forecast?lat={latitude}&lon={longitude}&appid={_apiKey}&units=imperial"
            Return Await GetAsync(url)
        End Function

        ''' <summary>
        ''' Get weather for stadium location at game time
        ''' </summary>
        Public Async Function GetGameDayWeatherAsync(stadium As StadiumLocation, gameTime As DateTime) As Task(Of String)
            ' For now, return current weather + forecast
            ' In production, this would interpolate forecast to game time
            
            Dim current = Await GetCurrentWeatherAsync(stadium.Latitude, stadium.Longitude)
            Dim forecast = Await GetForecastAsync(stadium.Latitude, stadium.Longitude)
            
            Return $"Stadium: {stadium.Name}{Environment.NewLine}" &
                   $"Game Time: {gameTime:yyyy-MM-dd HH:mm}{Environment.NewLine}" &
                   $"Current Weather:{Environment.NewLine}{current}{Environment.NewLine}{Environment.NewLine}" &
                   $"Forecast:{Environment.NewLine}{forecast}"
        End Function

    End Class

    ''' <summary>
    ''' Stadium location helper
    ''' </summary>
    Public Class StadiumLocation
        Public Property Name As String
        Public Property Latitude As Double
        Public Property Longitude As Double
        
        ' Common MLB stadiums
        Public Shared ReadOnly YankeeStadium As New StadiumLocation With {
            .Name = "Yankee Stadium",
            .Latitude = 40.8296,
            .Longitude = -73.9262
        }
        
        Public Shared ReadOnly FenwayPark As New StadiumLocation With {
            .Name = "Fenway Park",
            .Latitude = 42.3467,
            .Longitude = -71.0972
        }
        
        Public Shared ReadOnly DodgerStadium As New StadiumLocation With {
            .Name = "Dodger Stadium",
            .Latitude = 34.0739,
            .Longitude = -118.2400
        }
        
        ' NFL stadiums
        Public Shared ReadOnly SoFiStadium As New StadiumLocation With {
            .Name = "SoFi Stadium",
            .Latitude = 33.9535,
            .Longitude = -118.3392
        }
        
        Public Shared ReadOnly ArrowheadStadium As New StadiumLocation With {
            .Name = "Arrowhead Stadium",
            .Latitude = 39.0489,
            .Longitude = -94.4839
        }
    End Class

End Namespace
