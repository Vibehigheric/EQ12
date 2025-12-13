Imports System.Diagnostics
Imports System.IO
Imports System.Text.Json
Imports System.Windows.Forms

''' <summary>
''' EQ12 FOOD INTELLIGENCE DASHBOARD
''' VB.NET UI → Python food_profile + restaurant_finder bridge
''' Free tier: OpenStreetMap + Nominatim + OpenRouteService
''' </summary>
Public Class FoodDashboard
    Inherits Form
    
    Private txtFavCuisines As TextBox
    Private txtAvoidCuisines As TextBox
    Private numMaxDistance As NumericUpDown
    Private numMinPrice As NumericUpDown
    Private numMaxPrice As NumericUpDown
    Private numSpice As NumericUpDown
    Private numHealthyBias As NumericUpDown
    Private chkLateNight As CheckBox
    Private txtLocation As TextBox
    Private btnFindFood As Button
    Private lvResults As ListView
    Private rtbDetails As RichTextBox
    
    Public Sub New()
        InitializeComponents()
    End Sub
    
    Private Sub InitializeComponents()
        Me.Text = "EQ12 Food Intelligence Dashboard"
        Me.Size = New Size(900, 700)
        
        ' Layout controls
        Dim y As Integer = 20
        
        ' Favorite Cuisines
        AddLabel("Favorite Cuisines (comma-separated):", 20, y)
        txtFavCuisines = New TextBox With {.Location = New Point(20, y + 20), .Size = New Size(400, 25)}
        txtFavCuisines.Text = "Jamaican,Soul Food,Italian,Mexican"
        Me.Controls.Add(txtFavCuisines)
        y += 60
        
        ' Avoid Cuisines
        AddLabel("Avoid Cuisines:", 20, y)
        txtAvoidCuisines = New TextBox With {.Location = New Point(20, y + 20), .Size = New Size(400, 25)}
        txtAvoidCuisines.Text = "Sushi,Raw"
        Me.Controls.Add(txtAvoidCuisines)
        y += 60
        
        ' Location
        AddLabel("Location (ZIP or Address):", 20, y)
        txtLocation = New TextBox With {.Location = New Point(20, y + 20), .Size = New Size(400, 25)}
        txtLocation.Text = "14215"
        Me.Controls.Add(txtLocation)
        y += 60
        
        ' Distance slider
        AddLabel("Max Distance (km):", 20, y)
        numMaxDistance = New NumericUpDown With {
            .Location = New Point(20, y + 20),
            .Size = New Size(100, 25),
            .Minimum = 1,
            .Maximum = 20,
            .Value = 5,
            .DecimalPlaces = 1
        }
        Me.Controls.Add(numMaxDistance)
        y += 60
        
        ' Price range
        AddLabel("Price Range (1=cheap, 4=expensive):", 20, y)
        numMinPrice = New NumericUpDown With {
            .Location = New Point(20, y + 20),
            .Size = New Size(60, 25),
            .Minimum = 1,
            .Maximum = 4,
            .Value = 1
        }
        numMaxPrice = New NumericUpDown With {
            .Location = New Point(90, y + 20),
            .Size = New Size(60, 25),
            .Minimum = 1,
            .Maximum = 4,
            .Value = 2
        }
        Me.Controls.Add(numMinPrice)
        Me.Controls.Add(numMaxPrice)
        y += 60
        
        ' Spice tolerance
        AddLabel("Spice Tolerance (1-5):", 20, y)
        numSpice = New NumericUpDown With {
            .Location = New Point(20, y + 20),
            .Size = New Size(60, 25),
            .Minimum = 1,
            .Maximum = 5,
            .Value = 4
        }
        Me.Controls.Add(numSpice)
        y += 60
        
        ' Healthy bias
        AddLabel("Healthy Bias (0-1):", 20, y)
        numHealthyBias = New NumericUpDown With {
            .Location = New Point(20, y + 20),
            .Size = New Size(80, 25),
            .Minimum = 0,
            .Maximum = 1,
            .Value = 0.3D,
            .DecimalPlaces = 1,
            .Increment = 0.1D
        }
        Me.Controls.Add(numHealthyBias)
        y += 60
        
        ' Late night checkbox
        chkLateNight = New CheckBox With {
            .Location = New Point(20, y),
            .Size = New Size(200, 25),
            .Text = "Include late-night spots",
            .Checked = True
        }
        Me.Controls.Add(chkLateNight)
        y += 40
        
        ' Find Food button
        btnFindFood = New Button With {
            .Location = New Point(20, y),
            .Size = New Size(200, 40),
            .Text = "🍽️ FIND FOOD",
            .Font = New Font("Segoe UI", 12, FontStyle.Bold)
        }
        AddHandler btnFindFood.Click, AddressOf btnFindFood_Click
        Me.Controls.Add(btnFindFood)
        y += 60
        
        ' Results ListView
        lvResults = New ListView With {
            .Location = New Point(20, y),
            .Size = New Size(850, 200),
            .View = View.Details,
            .FullRowSelect = True
        }
        lvResults.Columns.Add("Restaurant", 200)
        lvResults.Columns.Add("Score", 60)
        lvResults.Columns.Add("Cuisines", 150)
        lvResults.Columns.Add("Distance (km)", 100)
        lvResults.Columns.Add("Price", 60)
        lvResults.Columns.Add("Rating", 80)
        Me.Controls.Add(lvResults)
        y += 220
        
        ' Details box
        rtbDetails = New RichTextBox With {
            .Location = New Point(20, y),
            .Size = New Size(850, 150),
            .ReadOnly = True
        }
        Me.Controls.Add(rtbDetails)
    End Sub
    
    Private Sub AddLabel(text As String, x As Integer, y As Integer)
        Dim lbl As New Label With {
            .Text = text,
            .Location = New Point(x, y),
            .Size = New Size(400, 20),
            .Font = New Font("Segoe UI", 10)
        }
        Me.Controls.Add(lbl)
    End Sub
    
    Private Sub btnFindFood_Click(sender As Object, e As EventArgs)
        Try
            lvResults.Items.Clear()
            rtbDetails.Clear()
            rtbDetails.AppendText("🔍 Searching for food recommendations..." & vbCrLf)
            Application.DoEvents()
            
            ' Build profile JSON
            Dim profileJson = BuildProfileJson()
            
            ' Call Python restaurant_finder.py
            Dim resultsJson = RunPythonFoodEngine(profileJson)
            
            ' Parse results
            Dim restaurants = JsonSerializer.Deserialize(Of List(Of RestaurantResult))(resultsJson)
            
            If restaurants IsNot Nothing AndAlso restaurants.Count > 0 Then
                DisplayResults(restaurants)
                rtbDetails.AppendText(vbCrLf & $"✅ Found {restaurants.Count} recommendations!")
            Else
                rtbDetails.AppendText(vbCrLf & "❌ No restaurants found. Try adjusting your criteria.")
            End If
            
        Catch ex As Exception
            MessageBox.Show($"Error: {ex.Message}", "Food Finder Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
            rtbDetails.AppendText(vbCrLf & $"❌ Error: {ex.Message}")
        End Try
    End Sub
    
    Private Function BuildProfileJson() As String
        Dim profile = New With {
            .favorite_cuisines = txtFavCuisines.Text.Split(","c).Select(Function(s) s.Trim()).ToArray(),
            .avoid_cuisines = txtAvoidCuisines.Text.Split(","c).Select(Function(s) s.Trim()).ToArray(),
            .max_distance_km = CDbl(numMaxDistance.Value),
            .min_price_level = CInt(numMinPrice.Value),
            .max_price_level = CInt(numMaxPrice.Value),
            .spice_tolerance = CInt(numSpice.Value),
            .late_night_ok = chkLateNight.Checked,
            .healthy_bias = CDbl(numHealthyBias.Value),
            .dietary_restrictions = New String() {}
        }
        Return JsonSerializer.Serialize(profile)
    End Function
    
    Private Function RunPythonFoodEngine(profileJson As String) As String
        Dim dataRoot = Path.GetFullPath(Path.Combine(Application.StartupPath, "..", "..", ".."))
        Dim pythonScript = Path.Combine(dataRoot, "scripts", "restaurant_finder.py")
        
        ' Build command
        Dim psi As New ProcessStartInfo()
        psi.FileName = "python"
        psi.Arguments = $"""{pythonScript}"" --location ""{txtLocation.Text}"" --top 5"
        psi.RedirectStandardInput = False
        psi.RedirectStandardOutput = True
        psi.RedirectStandardError = True
        psi.UseShellExecute = False
        psi.CreateNoWindow = True
        psi.WorkingDirectory = dataRoot
        
        Using p = Process.Start(psi)
            Dim output = p.StandardOutput.ReadToEnd()
            Dim errors = p.StandardError.ReadToEnd()
            p.WaitForExit()
            
            If p.ExitCode <> 0 Then
                Throw New Exception($"Python error: {errors}")
            End If
            
            ' Extract JSON from output (look for JSON array)
            Dim jsonStart = output.IndexOf("[")
            If jsonStart >= 0 Then
                Return output.Substring(jsonStart)
            Else
                Throw New Exception("No JSON results found in Python output")
            End If
        End Using
    End Function
    
    Private Sub DisplayResults(restaurants As List(Of RestaurantResult))
        For Each rest In restaurants
            Dim item = New ListViewItem(rest.name)
            item.SubItems.Add(rest.score.ToString("F1"))
            item.SubItems.Add(String.Join(", ", rest.cuisines))
            item.SubItems.Add(rest.distance_km.ToString("F2"))
            item.SubItems.Add(New String("$"c, rest.price_level))
            item.SubItems.Add($"⭐{rest.rating:F1}")
            item.Tag = rest
            lvResults.Items.Add(item)
        Next
        
        ' Show details of first result
        If restaurants.Count > 0 Then
            Dim top = restaurants(0)
            rtbDetails.AppendText(vbCrLf & vbCrLf)
            rtbDetails.AppendText($"🏆 TOP RECOMMENDATION:{vbCrLf}")
            rtbDetails.AppendText($"   {top.name} (Score: {top.score:F1}/10){vbCrLf}")
            rtbDetails.AppendText($"   Cuisines: {String.Join(", ", top.cuisines)}{vbCrLf}")
            rtbDetails.AppendText($"   Distance: {top.distance_km} km{vbCrLf}")
            rtbDetails.AppendText($"   Address: {top.address}{vbCrLf}")
        End If
    End Sub
End Class

Public Class RestaurantResult
    Public Property name As String
    Public Property score As Double
    Public Property cuisines As List(Of String)
    Public Property distance_km As Double
    Public Property price_level As Integer
    Public Property rating As Double
    Public Property address As String
    Public Property url As String
End Class
