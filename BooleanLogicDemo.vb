Module BooleanLogicDemo

    Sub Main()
        ' EQ12 SPORTS BETTING BOOLEAN LOGIC DEMONSTRATION
        ' ==============================================
        ' Professional Boolean logic application for sports betting automation

        Console.WriteLine("🏈 EQ12 SPORTS BETTING BOOLEAN LOGIC ENGINE")
        Console.WriteLine("=" & New String("="c, 50))
        Console.WriteLine()

        ' Define example Boolean variables for sports betting scenarios
        Dim IsUserLoggedIn As Boolean = True
        Dim HasAdminRights As Boolean = False
        Dim IsBettingWindowOpen As Boolean = True
        Dim IsMaintenanceMode As Boolean = True
        Dim HasSufficientBankroll As Boolean = True
        Dim IsVIPCustomer As Boolean = False
        Dim IsGameStarted As Boolean = False
        Dim HasLiveOdds As Boolean = True

        Console.WriteLine("📊 Current Betting System State:")
        Console.WriteLine("   User Logged In: " & IsUserLoggedIn)
        Console.WriteLine("   Admin Rights: " & HasAdminRights)
        Console.WriteLine("   Betting Window: " & IsBettingWindowOpen)
        Console.WriteLine("   Maintenance Mode: " & IsMaintenanceMode)
        Console.WriteLine("   Sufficient Bankroll: " & HasSufficientBankroll)
        Console.WriteLine("   VIP Customer: " & IsVIPCustomer)
        Console.WriteLine("   Game Started: " & IsGameStarted)
        Console.WriteLine("   Live Odds Available: " & HasLiveOdds)
        Console.WriteLine()

        ' --- 1. AND Operator (Requires ALL conditions to be True) ---
        Console.WriteLine("🔒 1. AND OPERATOR - All Conditions Must Be Met")
        Console.WriteLine(New String("-"c, 45))

        ' Check if user can place admin bets (requires login AND admin rights)
        If IsUserLoggedIn And HasAdminRights Then
            Console.WriteLine("✅ AND: User can place ADMIN bets (Logged in AND Admin)")
        Else
            Console.WriteLine("❌ AND: User CANNOT place admin bets (Missing: " &
                            If(Not IsUserLoggedIn, "Login ", "") &
                            If(Not HasAdminRights, "Admin Rights", "") & ")")
        End If

        ' Check if standard betting is available (multiple conditions)
        If IsUserLoggedIn And IsBettingWindowOpen And HasSufficientBankroll And Not IsMaintenanceMode Then
            Console.WriteLine("✅ AND: Standard betting is AVAILABLE")
        Else
            Console.WriteLine("❌ AND: Standard betting is BLOCKED")
            Console.WriteLine("      Missing conditions: " &
                            If(Not IsUserLoggedIn, "[Login] ", "") &
                            If(Not IsBettingWindowOpen, "[Window Open] ", "") &
                            If(Not HasSufficientBankroll, "[Bankroll] ", "") &
                            If(IsMaintenanceMode, "[No Maintenance] ", ""))
        End If

        Console.WriteLine(vbCrLf & "-----------------------------------")

        ' --- 2. OR Operator (Requires AT LEAST ONE to be True) ---
        Console.WriteLine("🚪 2. OR OPERATOR - Any Condition Can Allow Access")
        Console.WriteLine(New String("-"c, 45))

        ' Check if betting is allowed (window open OR admin override OR VIP access)
        If IsBettingWindowOpen Or HasAdminRights Or IsVIPCustomer Then
            Console.WriteLine("✅ OR: Betting is ALLOWED")
            Console.WriteLine("      Reason: " &
                            If(IsBettingWindowOpen, "[Window Open] ", "") &
                            If(HasAdminRights, "[Admin Override] ", "") &
                            If(IsVIPCustomer, "[VIP Access] ", ""))
        Else
            Console.WriteLine("❌ OR: Betting is DENIED - No access method available")
        End If

        ' Live betting availability (game started OR live odds available)
        If IsGameStarted Or HasLiveOdds Then
            Console.WriteLine("✅ OR: Live betting features available")
        Else
            Console.WriteLine("❌ OR: Live betting unavailable")
        End If

        Console.WriteLine(vbCrLf & "-----------------------------------")

        ' --- 3. NOT Operator (Inverts the value) ---
        Console.WriteLine("🔄 3. NOT OPERATOR - Logical Inversion")
        Console.WriteLine(New String("-"c, 45))

        ' Check if system is NOT in maintenance (inverted condition)
        If Not IsMaintenanceMode Then
            Console.WriteLine("✅ NOT: System is operational (NOT in maintenance)")
        Else
            Console.WriteLine("⚠️ NOT: System is under maintenance")
        End If

        ' Check if betting window is NOT closed
        If Not IsBettingWindowOpen Then
            Console.WriteLine("❌ NOT: Betting window is currently CLOSED")
        Else
            Console.WriteLine("✅ NOT: Betting window is OPEN")
        End If

        ' Security check: NOT admin but trying admin functions
        If IsUserLoggedIn And Not HasAdminRights Then
            Console.WriteLine("🔒 NOT: Regular user access (non-admin)")
        End If

        Console.WriteLine(vbCrLf & "-----------------------------------")

        ' --- 4. XOR Operator (Exclusive OR - Exactly ONE must be True) ---
        Console.WriteLine("⚖️ 4. XOR OPERATOR - Exactly One Condition")
        Console.WriteLine(New String("-"c, 45))

        ' Exclusive scenarios for maintenance vs normal operation
        If IsUserLoggedIn Xor IsMaintenanceMode Then
            Console.WriteLine("✅ XOR: Normal state - User OR Maintenance (not both)")
        Else
            Console.WriteLine("⚠️ XOR: Conflicted state - Both conditions match")
            Console.WriteLine("      User Logged: " & IsUserLoggedIn & ", Maintenance: " & IsMaintenanceMode)
        End If

        ' VIP vs Admin access (should be exclusive for security)
        If IsVIPCustomer Xor HasAdminRights Then
            Console.WriteLine("✅ XOR: Exclusive access type granted")
        Else
            If IsVIPCustomer And HasAdminRights Then
                Console.WriteLine("⚠️ XOR: SECURITY ALERT - Both VIP and Admin active")
            Else
                Console.WriteLine("❌ XOR: No special access granted")
            End If
        End If

        Console.WriteLine(vbCrLf & "-----------------------------------")

        ' --- 5. COMPLEX BOOLEAN COMBINATIONS ---
        Console.WriteLine("🎯 5. COMPLEX LOGIC - EQ12 Parlay Validation")
        Console.WriteLine(New String("-"c, 45))

        ' Complex parlay placement logic
        Dim CanPlaceParlay As Boolean = (IsUserLoggedIn And HasSufficientBankroll And IsBettingWindowOpen) And
                                       Not IsMaintenanceMode And
                                       (HasLiveOdds Or HasAdminRights)

        If CanPlaceParlay Then
            Console.WriteLine("🎰 ✅ PARLAY PLACEMENT: AUTHORIZED")
            Console.WriteLine("      All conditions satisfied for bet placement")
        Else
            Console.WriteLine("🎰 ❌ PARLAY PLACEMENT: BLOCKED")
            Console.WriteLine("      Check system requirements")
        End If

        ' Risk management logic
        Dim HighRiskBetting As Boolean = (Not IsVIPCustomer And HasSufficientBankroll) Or
                                        (HasAdminRights And IsBettingWindowOpen)

        If HighRiskBetting Then
            Console.WriteLine("⚠️ HIGH RISK: Enhanced monitoring enabled")
        End If

        ' Emergency access logic
        Dim EmergencyAccess As Boolean = HasAdminRights And (IsMaintenanceMode Or Not IsBettingWindowOpen)

        If EmergencyAccess Then
            Console.WriteLine("🚨 EMERGENCY: Admin override access granted")
        End If

        Console.WriteLine(vbCrLf & "-----------------------------------")
        Console.WriteLine("🏆 EQ12 BOOLEAN LOGIC DEMONSTRATION COMPLETE")
        Console.WriteLine("   Boolean operators successfully applied to sports betting logic")
        Console.WriteLine("   System ready for automated parlay generation")
        Console.WriteLine()

        ' Practical application summary
        Console.WriteLine("💡 PRACTICAL APPLICATIONS IN EQ12:")
        Console.WriteLine("   • Parlay validation using AND/OR combinations")
        Console.WriteLine("   • Risk management with NOT operators")
        Console.WriteLine("   • Exclusive access control with XOR")
        Console.WriteLine("   • Complex multi-condition betting rules")
        Console.WriteLine("   • Automated decision trees for bet placement")

        Console.WriteLine()
        Console.WriteLine("Press any key to continue...")
        Console.ReadKey()

    End Sub

End Module
