Imports System.Threading.Tasks
Imports System.IO
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq
Imports System.Net.Http
Imports System.Text
Imports Google.Apis.Auth.OAuth2
Imports Google.Cloud.BigQuery.V2
Imports Google.Cloud.Storage.V1
Imports Google.Cloud.SecretManager.V1
Imports Google.Apis.Auth.OAuth2.Flows
Imports Google.Apis.Auth.OAuth2.Responses

''' <summary>
''' Google Cloud Platform Authentication and Credential Management for EQ12
''' Handles service account authentication for BigQuery, Cloud Storage, and APIs
''' '''
Public Class GCPAuth
    Private ReadOnly _projectId As String
    Private ReadOnly _credentialsPath As String
    Private _credential As GoogleCredential

    Public Sub New(projectId As String, credentialsPath As String)
        _projectId = projectId
        _credentialsPath = credentialsPath

        LoadCredentials()
    End Sub

    ''' <summary>
    ''' Load Google Cloud credentials from JSON file
    ''' '''
    Private Sub LoadCredentials()
        Try
            If Not File.Exists(_credentialsPath) Then
                Throw New FileNotFoundException($"GCP credentials file not found: {_credentialsPath}")
            End If

            Environment.SetEnvironmentVariable("GOOGLE_APPLICATION_CREDENTIALS", _credentialsPath)
            _credential = GoogleCredential.FromFile(_credentialsPath)

            Console.WriteLine($"✅ GCP credentials loaded from {_credentialsPath}")

        Catch ex As Exception
            Console.WriteLine($"❌ GCP authentication failed: {ex.Message}")
            Throw
        End Try
    End Sub

    ''' <summary>
    ''' Get authenticated BigQuery client
    ''' '''
    Public Function GetBigQueryClient() As BigQueryClient
        Try
            Return BigQueryClient.Create(_projectId, _credential)
        Catch ex As Exception
            Console.WriteLine($"❌ BigQuery client creation failed: {ex.Message}")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Get authenticated Cloud Storage client
    ''' '''
    Public Function GetStorageClient() As StorageClient
        Try
            Return StorageClient.Create(_credential)
        Catch ex As Exception
            Console.WriteLine($"❌ Storage client creation failed: {ex.Message}")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Get Secret Manager client
    ''' '''
    Public Function GetSecretManagerClient() As SecretManagerServiceClient
        Try
            Return SecretManagerServiceClient.Create(_credential)
        Catch ex As Exception
            Console.WriteLine($"❌ Secret Manager client creation failed: {ex.Message}")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Retrieve secret from Secret Manager
    ''' '''
    Public Function GetSecret(secretName As String) As String
        Try
            Dim client = GetSecretManagerClient()
            Dim secretVersionName = New SecretVersionName(_projectId, secretName, "latest")
            Dim response = client.AccessSecretVersion(secretVersionName)
            Return response.Payload.Data.ToStringUtf8()

        Catch ex As Exception
            Console.WriteLine($"❌ Secret retrieval failed for {secretName}: {ex.Message}")
            Return ""
        End Try
    End Function

    ''' <summary>
    ''' Get access token for API calls (enhanced for Gemini Cloud Chat)
    ''' '''
    Public Async Function GetAccessTokenAsync() As Task(Of String)
        Try
            Dim scopedCredential = _credential.CreateScoped(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/generative-language.readonly",
                "https://www.googleapis.com/auth/cloud-console"
            )

            Dim token = Await scopedCredential.UnderlyingCredential.GetAccessTokenForRequestAsync()
            Return token

        Catch ex As Exception
            Console.WriteLine($"❌ Access token retrieval failed: {ex.Message}")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Get OAuth2 token specifically for Gemini Cloud Chat Assistant
    ''' '''
    Public Async Function GetGeminiCloudTokenAsync() As Task(Of String)
        Try
            Dim scopedCredential = _credential.CreateScoped(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/cloud-console",
                "https://www.googleapis.com/auth/generative-language"
            )

            Dim token = Await scopedCredential.UnderlyingCredential.GetAccessTokenForRequestAsync()
            Console.WriteLine("✅ Gemini Cloud Chat token acquired")
            Return token

        Catch ex As Exception
            Console.WriteLine($"❌ Gemini Cloud token retrieval failed: {ex.Message}")
            Return ""
        End Try
    End Function

    ''' <summary>
    ''' Validate GCP configuration and connectivity
    ''' '''
    Public Async Function ValidateConnectionAsync() As Task(Of Boolean)
        Try
            ' Test BigQuery access
            Dim bqClient = GetBigQueryClient()
            Dim datasets = bqClient.ListDatasets().Take(1).ToList()

            ' Test Storage access
            Dim storageClient = GetStorageClient()
            Dim buckets = storageClient.ListBuckets(_projectId).Take(1).ToList()

            Console.WriteLine($"✅ GCP connection validated for project {_projectId}")
            Return True

        Catch ex As Exception
            Console.WriteLine($"❌ GCP connection validation failed: {ex.Message}")
            Return False
        End Try
    End Function

    Public ReadOnly Property ProjectId As String
        Get
            Return _projectId
        End Get
    End Property

    Public ReadOnly Property Credential As GoogleCredential
        Get
            Return _credential
        End Get
    End Property
End Class
