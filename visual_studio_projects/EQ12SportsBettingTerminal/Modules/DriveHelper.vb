Imports System.IO
Imports System.Net.Http
Imports System.Text
Imports Newtonsoft.Json.Linq
Imports Newtonsoft.Json
Imports System.Web

''' <summary>
''' Drive Helper - Google Drive API Integration
''' Handles file upload, management, and DocHub integration for EQ12 reports
''' Features: PDF upload, DocHub URL generation, Bitly shortening, metadata management
''' </summary>
Public Class DriveHelper

    ''' <summary>
    ''' Upload report file to Google Drive and return file ID
    ''' </summary>
    ''' <param name="config">Configuration object with Google Drive settings</param>
    ''' <param name="localPath">Local file path to upload</param>
    ''' <param name="fileName">Display name for file in Drive (optional)</param>
    ''' <param name="folderId">Google Drive folder ID (optional)</param>
    ''' <returns>Google Drive file ID or error message</returns>
    Public Shared Function UploadReport(config As JObject, localPath As String,
                                       Optional fileName As String = Nothing,
                                       Optional folderId As String = Nothing) As String
        Try
            Console.WriteLine($"📤 Uploading {Path.GetFileName(localPath)} to Google Drive...")

            ' Validate inputs
            If Not File.Exists(localPath) Then
                Return $"Error: File not found: {localPath}"
            End If

            ' Get access token
            Dim accessToken = GoogleAuthHelper.GetAccessToken(config, "drive")
            If accessToken.StartsWith("Error") Then
                Return accessToken
            End If

            ' Use provided filename or extract from path
            If String.IsNullOrEmpty(fileName) Then
                fileName = Path.GetFileName(localPath)
            End If

            ' Use configured folder ID if not specified
            If String.IsNullOrEmpty(folderId) Then
                folderId = config("google_drive")("folder_id")?.ToString()
            End If

            ' Read file content
            Dim fileBytes = File.ReadAllBytes(localPath)
            Dim mimeType = GetMimeType(localPath)

            ' Prepare metadata
            Dim metadata As New JObject()
            metadata("name") = fileName
            If Not String.IsNullOrEmpty(folderId) Then
                metadata("parents") = New JArray({folderId})
            End If

            ' Upload using multipart request
            Using client As New HttpClient()
                client.DefaultRequestHeaders.Add("Authorization", $"Bearer {accessToken}")

                ' Create multipart content
                Using multipartContent As New MultipartFormDataContent()
                    ' Add metadata part
                    Dim metadataContent = New StringContent(metadata.ToString(), Encoding.UTF8, "application/json")
                    multipartContent.Add(metadataContent, "metadata")

                    ' Add file content part
                    Dim fileContent = New ByteArrayContent(fileBytes)
                    fileContent.Headers.ContentType = New Headers.MediaTypeHeaderValue(mimeType)
                    multipartContent.Add(fileContent, "file", fileName)

                    ' Upload to Google Drive
                    Dim uploadUrl = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
                    Dim response = client.PostAsync(uploadUrl, multipartContent).Result

                    If response.IsSuccessStatusCode Then
                        Dim responseContent = response.Content.ReadAsStringAsync().Result
                        Dim uploadResult = JObject.Parse(responseContent)
                        Dim fileId = uploadResult("id")?.ToString()

                        If Not String.IsNullOrEmpty(fileId) Then
                            Console.WriteLine($"✅ Upload successful! File ID: {fileId}")

                            ' Log upload to database
                            LogDriveUpload(localPath, fileId, fileName)

                            Return fileId
                        Else
                            Return "Error: No file ID returned from upload"
                        End If
                    Else
                        Dim errorContent = response.Content.ReadAsStringAsync().Result
                        Return $"Error: Upload failed - {response.StatusCode}: {errorContent}"
                    End If
                End Using
            End Using

        Catch ex As Exception
            Return $"Error uploading file: {ex.Message}"
        End Try
    End Function

    ''' <summary>
    ''' Generate DocHub URL for editing uploaded PDF
    ''' </summary>
    ''' <param name="config">Configuration object</param>
    ''' <param name="fileId">Google Drive file ID</param>
    ''' <returns>DocHub edit URL</returns>
    Public Shared Function GetDocHubUrl(config As JObject, fileId As String) As String
        Try
            Dim baseUrl = config("dochub")("base_url")?.ToString() ?? "https://dochub.com/edit/"

            ' DocHub integration methods:
            ' Method 1: Direct Drive file ID (if DocHub supports)
            ' Method 2: Share link conversion
            ' Method 3: Custom integration URL

            Dim docHubUrl = baseUrl & fileId

            Console.WriteLine($"📝 DocHub URL generated: {docHubUrl}")

            Return docHubUrl

        Catch ex As Exception
            Return $"Error generating DocHub URL: {ex.Message}"
        End Try
    End Function

    ''' <summary>
    ''' Get shareable Google Drive link for file
    ''' </summary>
    ''' <param name="config">Configuration object</param>
    ''' <param name="fileId">Google Drive file ID</param>
    ''' <param name="shareType">Share type: 'view', 'edit', or 'comment'</param>
    ''' <returns>Shareable URL</returns>
    Public Shared Function GetShareableLink(config As JObject, fileId As String,
                                          Optional shareType As String = "view") As String
        Try
            Dim accessToken = GoogleAuthHelper.GetAccessToken(config, "drive")
            If accessToken.StartsWith("Error") Then
                Return accessToken
            End If

            ' Make file publicly accessible
            Dim permissionResult = SetFilePermissions(config, fileId, "anyone", "reader")
            If permissionResult.StartsWith("Error") Then
                Console.WriteLine($"⚠️ Warning: Could not set public permissions: {permissionResult}")
            End If

            ' Generate shareable URL
            Dim shareUrl As String
            Select Case shareType.ToLower()
                Case "edit"
                    shareUrl = $"https://drive.google.com/file/d/{fileId}/edit"
                Case "comment"
                    shareUrl = $"https://drive.google.com/file/d/{fileId}/comment"
                Case Else ' "view"
                    shareUrl = $"https://drive.google.com/file/d/{fileId}/view"
            End Select

            Return shareUrl

        Catch ex As Exception
            Return $"Error generating shareable link: {ex.Message}"
        End Try
    End Function

    ''' <summary>
    ''' Upload report with complete workflow: Drive upload + DocHub URL + Bitly shortening
    ''' </summary>
    ''' <param name="config">Configuration object</param>
    ''' <param name="localPath">Local file path to upload</param>
    ''' <returns>Dictionary with fileId, docHubUrl, bitlyUrl, and shareableUrl</returns>
    Public Shared Function UploadReportWithWorkflow(config As JObject, localPath As String) As Dictionary(Of String, String)
        Dim result As New Dictionary(Of String, String)

        Try
            Console.WriteLine($"🚀 Starting complete upload workflow for {Path.GetFileName(localPath)}")

            ' Step 1: Upload to Google Drive
            Dim fileId = UploadReport(config, localPath)
            If fileId.StartsWith("Error") Then
                result("error") = fileId
                Return result
            End If
            result("fileId") = fileId

            ' Step 2: Generate DocHub URL
            Dim docHubUrl = GetDocHubUrl(config, fileId)
            result("docHubUrl") = docHubUrl

            ' Step 3: Get shareable link
            Dim shareableUrl = GetShareableLink(config, fileId, "view")
            If Not shareableUrl.StartsWith("Error") Then
                result("shareableUrl") = shareableUrl
            End If

            ' Step 4: Shorten URLs with Bitly (if available)
            If config("bitly")?.ContainsKey("token") = True Then
                Try
                    ' Shorten DocHub URL
                    Dim docHubBitly = BitlyHelper.ShortenUrl(config, docHubUrl, $"DocHub: {Path.GetFileNameWithoutExtension(localPath)}")
                    If Not docHubBitly.StartsWith("Error") Then
                        result("docHubBitlyUrl") = docHubBitly
                    End If

                    ' Shorten shareable URL
                    If result.ContainsKey("shareableUrl") Then
                        Dim shareableBitly = BitlyHelper.ShortenUrl(config, shareableUrl, $"Drive: {Path.GetFileNameWithoutExtension(localPath)}")
                        If Not shareableBitly.StartsWith("Error") Then
                            result("shareableBitlyUrl") = shareableBitly
                        End If
                    End If
                Catch ex As Exception
                    Console.WriteLine($"⚠️ Bitly shortening failed: {ex.Message}")
                End Try
            End If

            ' Step 5: Update database with complete information
            UpdateDriveUpload(fileId, docHubUrl, result.GetValueOrDefault("docHubBitlyUrl", ""),
                            result.GetValueOrDefault("shareableUrl", ""), result.GetValueOrDefault("shareableBitlyUrl", ""))

            Console.WriteLine("✅ Upload workflow completed successfully!")

            Return result

        Catch ex As Exception
            result("error") = $"Upload workflow failed: {ex.Message}"
            Return result
        End Try
    End Function

    ''' <summary>
    ''' Set file permissions for sharing
    ''' </summary>
    Private Shared Function SetFilePermissions(config As JObject, fileId As String,
                                             type As String, role As String) As String
        Try
            Dim accessToken = GoogleAuthHelper.GetAccessToken(config, "drive")
            If accessToken.StartsWith("Error") Then
                Return accessToken
            End If

            Dim permissionData As New JObject()
            permissionData("type") = type
            permissionData("role") = role

            Using client As New HttpClient()
                client.DefaultRequestHeaders.Add("Authorization", $"Bearer {accessToken}")

                Dim content = New StringContent(permissionData.ToString(), Encoding.UTF8, "application/json")
                Dim permissionUrl = $"https://www.googleapis.com/drive/v3/files/{fileId}/permissions"
                Dim response = client.PostAsync(permissionUrl, content).Result

                If response.IsSuccessStatusCode Then
                    Return "Success"
                Else
                    Dim errorContent = response.Content.ReadAsStringAsync().Result
                    Return $"Error: {response.StatusCode} - {errorContent}"
                End If
            End Using

        Catch ex As Exception
            Return $"Error setting permissions: {ex.Message}"
        End Try
    End Function

    ''' <summary>
    ''' Get MIME type for file extension
    ''' </summary>
    Private Shared Function GetMimeType(filePath As String) As String
        Dim extension = Path.GetExtension(filePath).ToLower()

        Select Case extension
            Case ".pdf"
                Return "application/pdf"
            Case ".xlsx"
                Return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            Case ".xls"
                Return "application/vnd.ms-excel"
            Case ".docx"
                Return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            Case ".doc"
                Return "application/msword"
            Case ".txt"
                Return "text/plain"
            Case ".json"
                Return "application/json"
            Case ".csv"
                Return "text/csv"
            Case Else
                Return "application/octet-stream"
        End Select
    End Function

    ''' <summary>
    ''' List files in Google Drive folder
    ''' </summary>
    ''' <param name="config">Configuration object</param>
    ''' <param name="folderId">Folder ID to list (optional)</param>
    ''' <param name="maxResults">Maximum number of files to return</param>
    ''' <returns>List of file information</returns>
    Public Shared Function ListFiles(config As JObject, Optional folderId As String = Nothing,
                                   Optional maxResults As Integer = 100) As List(Of Dictionary(Of String, String))
        Dim fileList As New List(Of Dictionary(Of String, String))

        Try
            Dim accessToken = GoogleAuthHelper.GetAccessToken(config, "drive")
            If accessToken.StartsWith("Error") Then
                Console.WriteLine($"❌ {accessToken}")
                Return fileList
            End If

            ' Build query
            Dim query = ""
            If Not String.IsNullOrEmpty(folderId) Then
                query = $"'{folderId}' in parents"
            End If

            Dim listUrl = "https://www.googleapis.com/drive/v3/files" &
                         "?fields=files(id,name,mimeType,size,createdTime,modifiedTime)" &
                         $"&pageSize={maxResults}"

            If Not String.IsNullOrEmpty(query) Then
                listUrl &= "&q=" & HttpUtility.UrlEncode(query)
            End If

            Using client As New HttpClient()
                client.DefaultRequestHeaders.Add("Authorization", $"Bearer {accessToken}")

                Dim response = client.GetAsync(listUrl).Result

                If response.IsSuccessStatusCode Then
                    Dim responseContent = response.Content.ReadAsStringAsync().Result
                    Dim listResult = JObject.Parse(responseContent)

                    If listResult("files") IsNot Nothing Then
                        For Each file In listResult("files")
                            Dim fileInfo As New Dictionary(Of String, String) From {
                                {"id", file("id")?.ToString() ?? ""},
                                {"name", file("name")?.ToString() ?? ""},
                                {"mimeType", file("mimeType")?.ToString() ?? ""},
                                {"size", file("size")?.ToString() ?? "0"},
                                {"createdTime", file("createdTime")?.ToString() ?? ""},
                                {"modifiedTime", file("modifiedTime")?.ToString() ?? ""}
                            }
                            fileList.Add(fileInfo)
                        Next
                    End If
                End If
            End Using

        Catch ex As Exception
            Console.WriteLine($"❌ Error listing files: {ex.Message}")
        End Try

        Return fileList
    End Function

    ''' <summary>
    ''' Log drive upload to database
    ''' </summary>
    Private Shared Sub LogDriveUpload(localPath As String, driveId As String, fileName As String)
        Try
            Using conn As New System.Data.SQLite.SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()

                Dim sql = "INSERT INTO drive_uploads (ts, local_path, drive_id, file_name, created_at) " &
                         "VALUES (@ts, @local_path, @drive_id, @file_name, @created_at)"

                Using cmd As New System.Data.SQLite.SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@ts", DateTime.UtcNow)
                    cmd.Parameters.AddWithValue("@local_path", localPath)
                    cmd.Parameters.AddWithValue("@drive_id", driveId)
                    cmd.Parameters.AddWithValue("@file_name", fileName)
                    cmd.Parameters.AddWithValue("@created_at", DateTime.UtcNow)

                    cmd.ExecuteNonQuery()
                End Using
            End Using
        Catch ex As Exception
            Console.WriteLine($"⚠️ Failed to log drive upload: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Update drive upload record with additional URLs
    ''' </summary>
    Private Shared Sub UpdateDriveUpload(driveId As String, docHubUrl As String,
                                       docHubBitlyUrl As String, shareableUrl As String,
                                       shareableBitlyUrl As String)
        Try
            Using conn As New System.Data.SQLite.SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()

                Dim sql = "UPDATE drive_uploads SET dochub_url = @dochub_url, " &
                         "dochub_bitly_url = @dochub_bitly_url, shareable_url = @shareable_url, " &
                         "shareable_bitly_url = @shareable_bitly_url " &
                         "WHERE drive_id = @drive_id"

                Using cmd As New System.Data.SQLite.SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@dochub_url", docHubUrl)
                    cmd.Parameters.AddWithValue("@dochub_bitly_url", docHubBitlyUrl)
                    cmd.Parameters.AddWithValue("@shareable_url", shareableUrl)
                    cmd.Parameters.AddWithValue("@shareable_bitly_url", shareableBitlyUrl)
                    cmd.Parameters.AddWithValue("@drive_id", driveId)

                    cmd.ExecuteNonQuery()
                End Using
            End Using
        Catch ex As Exception
            Console.WriteLine($"⚠️ Failed to update drive upload: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Test Google Drive connectivity and permissions
    ''' </summary>
    ''' <param name="config">Configuration object</param>
    ''' <returns>Test result message</returns>
    Public Shared Function TestDriveConnection(config As JObject) As String
        Try
            ' Test authentication
            Dim authTest = GoogleAuthHelper.TestConnection(config, "drive")
            If authTest.StartsWith("❌") Then
                Return authTest
            End If

            ' Test file listing (basic API call)
            Dim files = ListFiles(config, Nothing, 5)

            Return $"✅ Google Drive connection successful - Found {files.Count} recent files"

        Catch ex As Exception
            Return $"❌ Google Drive test failed: {ex.Message}"
        End Try
    End Function
End Class
