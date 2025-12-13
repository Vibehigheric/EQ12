Option Strict On
Option Explicit On

Imports System.Net.Http
Imports System.Threading.Tasks

Namespace EQ12.Core.ApiClient

    ''' <summary>
    ''' Client for Hugging Face Hub API (metadata and inference)
    ''' </summary>
    Public Class HuggingFaceClient
        Inherits ApiClientBase

        Public Sub New(Optional token As String = Nothing)
            Dim catalog As New ApiCatalog()
            Dim apiInfo = catalog.FindByName("Hugging Face Hub (Metadata)")
            
            MyBase.New(apiInfo, token)
        End Sub

        ''' <summary>
        ''' Test connection by fetching top 5 models
        ''' </summary>
        Public Overrides Async Function TestConnectionAsync() As Task(Of String)
            Dim url = "models?limit=5&sort=downloads&direction=-1"
            Dim response = Await GetAsync(url)
            
            Return $"✅ {ApiInfo.Name} - Status: Connected{Environment.NewLine}" &
                   $"Response preview:{Environment.NewLine}" &
                   response.Substring(0, Math.Min(500, response.Length))
        End Function

        ''' <summary>
        ''' Search for models by task (e.g., "text-classification", "question-answering")
        ''' </summary>
        Public Async Function SearchModelsAsync(task As String, Optional limit As Integer = 10) As Task(Of String)
            Dim url = $"models?filter={task}&limit={limit}&sort=downloads&direction=-1"
            Return Await GetAsync(url)
        End Function

        ''' <summary>
        ''' Get model details by model ID (e.g., "gpt2", "bert-base-uncased")
        ''' </summary>
        Public Async Function GetModelInfoAsync(modelId As String) As Task(Of String)
            Dim url = $"models/{modelId}"
            Return Await GetAsync(url)
        End Function

        ''' <summary>
        ''' Search datasets
        ''' </summary>
        Public Async Function SearchDatasetsAsync(query As String, Optional limit As Integer = 10) As Task(Of String)
            Dim url = $"datasets?search={Uri.EscapeDataString(query)}&limit={limit}"
            Return Await GetAsync(url)
        End Function

    End Class

    ''' <summary>
    ''' Client for Hugging Face Inference API (serverless model execution)
    ''' </summary>
    Public Class HuggingFaceInferenceClient
        Inherits ApiClientBase

        Public Sub New(Optional token As String = Nothing)
            Dim catalog As New ApiCatalog()
            Dim apiInfo = catalog.FindByName("Hugging Face Inference (Serverless)")
            
            ' Override base URL for inference API
            apiInfo.BaseUrl = "https://api-inference.huggingface.co"
            
            MyBase.New(apiInfo, token)
        End Sub

        Public Overrides Async Function TestConnectionAsync() As Task(Of String)
            ' Test with a simple sentiment analysis model
            Dim modelId = "distilbert-base-uncased-finetuned-sst-2-english"
            Dim result = Await ClassifyTextAsync(modelId, "I love sports betting automation!")
            
            Return $"✅ {ApiInfo.Name} - Status: Connected{Environment.NewLine}" &
                   $"Test classification result:{Environment.NewLine}{result}"
        End Function

        ''' <summary>
        ''' Run text classification inference
        ''' </summary>
        Public Async Function ClassifyTextAsync(modelId As String, text As String) As Task(Of String)
            Dim url = $"models/{modelId}"
            Dim jsonContent = $"{{""inputs"": ""{text.Replace("""", "\""")}}""}}"
            Dim content As New StringContent(jsonContent, Text.Encoding.UTF8, "application/json")
            
            Return Await PostAsync(url, content)
        End Function

        ''' <summary>
        ''' Generate text embeddings for similarity/search
        ''' </summary>
        Public Async Function GetEmbeddingsAsync(modelId As String, text As String) As Task(Of String)
            Dim url = $"models/{modelId}"
            Dim jsonContent = $"{{""inputs"": ""{text.Replace("""", "\""")}}""}}"
            Dim content As New StringContent(jsonContent, Text.Encoding.UTF8, "application/json")
            
            Return Await PostAsync(url, content)
        End Function

    End Class

End Namespace
