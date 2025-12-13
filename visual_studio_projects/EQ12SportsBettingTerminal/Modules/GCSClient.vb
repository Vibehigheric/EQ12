Imports System.Threading.Tasks
Imports System.IO
Imports Google.Cloud.Storage.V1
Imports System.Collections.Generic

''' <summary>
''' Google Cloud Storage Client for EQ12
''' Handles file uploads, downloads, and management for reports and deliverables
''' '''
Public Class GCSClient
    Private ReadOnly _client As StorageClient
    Private ReadOnly _projectId As String
    Private ReadOnly _bucketName As String

    Public Sub New(gcpAuth As GCPAuth, bucketName As String)
        _client = gcpAuth.GetStorageClient()
        _projectId = gcpAuth.ProjectId
        _bucketName = bucketName

        EnsureBucketExists()
    End Sub

    ''' <summary>
    ''' Ensure storage bucket exists
    ''' '''
    Private Sub EnsureBucketExists()
        Try
            _client.GetBucket(_bucketName)
            Console.WriteLine($"✅ Storage bucket {_bucketName} ready")

        Catch ex As GoogleApiException When ex.HttpStatusCode = Net.HttpStatusCode.NotFound
            ' Create bucket if it doesn't exist
            Try
                _client.CreateBucket(_projectId, New Bucket With {
                    .Name = _bucketName,
                    .Location = "US",
                    .StorageClass = "STANDARD"
                })

                Console.WriteLine($"✅ Created storage bucket {_bucketName}")

            Catch createEx As Exception
                Console.WriteLine($"❌ Bucket creation failed: {createEx.Message}")
                Throw
            End Try

        Catch ex As Exception
            Console.WriteLine($"❌ Storage validation failed: {ex.Message}")
            Throw
        End Try
    End Sub

    ''' <summary>
    ''' Upload file to Cloud Storage
    ''' '''
    Public Function UploadFile(localFilePath As String, cloudFileName As String, Optional contentType As String = "application/octet-stream") As String
        Try
            If Not File.Exists(localFilePath) Then
                Throw New FileNotFoundException($"Local file not found: {localFilePath}")
            End If

            Using fileStream = File.OpenRead(localFilePath)
                Dim obj = _client.UploadObject(_bucketName, cloudFileName, contentType, fileStream)

                Dim publicUrl = $"https://storage.googleapis.com/{_bucketName}/{cloudFileName}"
                Console.WriteLine($"✅ Uploaded {localFilePath} to {publicUrl}")

                Return publicUrl
            End Using

        Catch ex As Exception
            Console.WriteLine($"❌ File upload failed: {ex.Message}")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Upload text content directly to Cloud Storage
    ''' '''
    Public Function UploadText(content As String, cloudFileName As String, Optional contentType As String = "text/plain") As String
        Try
            Using memStream = New MemoryStream(System.Text.Encoding.UTF8.GetBytes(content))
                Dim obj = _client.UploadObject(_bucketName, cloudFileName, contentType, memStream)

                Dim publicUrl = $"https://storage.googleapis.com/{_bucketName}/{cloudFileName}"
                Console.WriteLine($"✅ Uploaded text content to {publicUrl}")

                Return publicUrl
            End Using

        Catch ex As Exception
            Console.WriteLine($"❌ Text upload failed: {ex.Message}")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Download file from Cloud Storage
    ''' '''
    Public Sub DownloadFile(cloudFileName As String, localFilePath As String)
        Try
            Using fileStream = File.Create(localFilePath)
                _client.DownloadObject(_bucketName, cloudFileName, fileStream)
            End Using

            Console.WriteLine($"✅ Downloaded {cloudFileName} to {localFilePath}")

        Catch ex As Exception
            Console.WriteLine($"❌ File download failed: {ex.Message}")
            Throw
        End Try
    End Sub

    ''' <summary>
    ''' Get download URL for a file
    ''' '''
    Public Function GetDownloadUrl(cloudFileName As String, Optional expirationHours As Integer = 24) As String
        Try
            Dim obj = _client.GetObject(_bucketName, cloudFileName)

            ' Generate signed URL for temporary access
            Dim expiration = DateTimeOffset.UtcNow.AddHours(expirationHours)
            Dim signedUrl = _client.CreateSignedUrl(_bucketName, cloudFileName, expiration)

            Console.WriteLine($"✅ Generated download URL for {cloudFileName} (expires: {expiration})")
            Return signedUrl

        Catch ex As Exception
            Console.WriteLine($"❌ URL generation failed: {ex.Message}")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' List files in bucket with optional prefix filter
    ''' '''
    Public Function ListFiles(Optional prefix As String = "") As List(Of String)
        Try
            Dim options As New ListObjectsOptions With {
                .Prefix = prefix
            }

            Dim objects = _client.ListObjects(_bucketName, options)
            Dim fileNames As New List(Of String)()

            For Each obj In objects
                fileNames.Add(obj.Name)
            Next

            Console.WriteLine($"✅ Found {fileNames.Count} files with prefix '{prefix}'")
            Return fileNames

        Catch ex As Exception
            Console.WriteLine($"❌ File listing failed: {ex.Message}")
            Return New List(Of String)()
        End Try
    End Function

    ''' <summary>
    ''' Delete file from Cloud Storage
    ''' '''
    Public Sub DeleteFile(cloudFileName As String)
        Try
            _client.DeleteObject(_bucketName, cloudFileName)
            Console.WriteLine($"✅ Deleted {cloudFileName}")

        Catch ex As Exception
            Console.WriteLine($"❌ File deletion failed: {ex.Message}")
            Throw
        End Try
    End Sub

    ''' <summary>
    ''' Upload EQ12 analytics report with structured naming
    ''' '''
    Public Function UploadAnalyticsReport(reportType As String, content As String, Optional format As String = "html") As String
        Dim timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss")
        Dim fileName = $"eq12_reports/{reportType}_{timestamp}.{format}"

        Dim contentType = If(format = "html", "text/html", If(format = "json", "application/json", "text/plain"))

        Return UploadText(content, fileName, contentType)
    End Function

    ''' <summary>
    ''' Upload monetization deliverable with affiliate tracking
    ''' '''
    Public Function UploadMonetizationDeliverable(deliverableType As String, content As String, affiliateId As String) As String
        Dim timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss")
        Dim fileName = $"monetization/{deliverableType}_aff{affiliateId}_{timestamp}.html"

        Return UploadText(content, fileName, "text/html")
    End Function

    Public ReadOnly Property BucketName As String
        Get
            Return _bucketName
        End Get
    End Property
End Class
