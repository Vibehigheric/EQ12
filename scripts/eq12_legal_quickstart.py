#!/usr/bin/env python3
"""
EQ12 LEGAL DOCUMENT GENERATOR - QUICK START
Simple interface for generating legal documents with AI
"""

import asyncio
import sys
from eq12_legal_prompt_executor import LegalPromptExecutor

async def main():
    print("="*80)
    print("🏛️  EQ12 LEGAL DOCUMENT GENERATOR")
    print("   AI-Powered Legal Document Automation")
    print("="*80)
    print()
    
    # Initialize
    executor = LegalPromptExecutor()
    executor.initialize_database()
    
    if not executor.ai_providers:
        print("❌ No AI providers configured!")
        print("\nPlease set one of these environment variables:")
        print("   OPENROUTER_API_KEY  (recommended)")
        print("   ANTHROPIC_API_KEY")
        print("   GROQ_API_KEY")
        print("   OPENAI_API_KEY")
        return
    
    print(f"✅ {len(executor.ai_providers)} AI providers ready")
    print(f"🤖 Using: {executor.primary_provider}")
    print()
    
    # Menu
    print("AVAILABLE DOCUMENT TYPES:")
    print()
    print("1. Credit Dispute Letter (FCRA violation for dismissed lawsuit)")
    print("2. Motion to Dismiss (FRCP 12(b)(6) - failure to state claim)")
    print("3. Motion for Summary Judgment (FRCP 56)")
    print("4. PACER Case Analysis (comprehensive docket review)")
    print("5. Debt Validation Request (FDCPA 1692g)")
    print("6. Custom Prompt (enter prompt number 1-1000)")
    print()
    
    choice = input("Select document type (1-6): ").strip()
    print()
    
    if choice == "1":
        # Credit Dispute Letter
        print("CREDIT DISPUTE LETTER")
        print("-" * 40)
        case_number = input("Case Number (e.g., 1:23-cv-12345): ").strip()
        debt_collector = input("Debt Collector Name: ").strip()
        dismissal_date = input("Dismissal Date (e.g., October 15, 2025): ").strip()
        credit_bureau = input("Credit Bureau (Equifax/Experian/TransUnion): ").strip()
        
        print("\n⏳ Generating credit dispute letter...")
        result = await executor.generate_credit_dispute_letter(
            case_number=case_number,
            debt_collector=debt_collector,
            dismissal_date=dismissal_date,
            credit_bureau=credit_bureau,
            client_id="quickstart_user"
        )
    
    elif choice == "2":
        # Motion to Dismiss
        print("MOTION TO DISMISS")
        print("-" * 40)
        case_number = input("Case Number: ").strip()
        claim_type = input("Claim Type (e.g., breach of contract): ").strip()
        missing_element = input("Missing Element (e.g., consideration): ").strip()
        
        print("\n⏳ Generating motion to dismiss...")
        result = await executor.generate_motion_to_dismiss(
            case_number=case_number,
            claim_type=claim_type,
            missing_element=missing_element,
            client_id="quickstart_user"
        )
    
    elif choice == "3":
        # Motion for Summary Judgment
        print("MOTION FOR SUMMARY JUDGMENT")
        print("-" * 40)
        case_number = input("Case Number: ").strip()
        issue = input("Issue (no genuine dispute regarding): ").strip()
        
        print("\n⏳ Generating motion for summary judgment...")
        result = await executor.generate_document(
            402,
            {'CASE_NUMBER': case_number, 'ISSUE': issue},
            client_id="quickstart_user"
        )
    
    elif choice == "4":
        # PACER Case Analysis
        print("PACER CASE ANALYSIS")
        print("-" * 40)
        case_number = input("Case Number: ").strip()
        district = input("District (e.g., Northern District of California): ").strip()
        
        print("\n⏳ Analyzing PACER case...")
        result = await executor.analyze_pacer_case(
            case_number=case_number,
            district=district,
            client_id="quickstart_user"
        )
    
    elif choice == "5":
        # Debt Validation Request
        print("DEBT VALIDATION REQUEST")
        print("-" * 40)
        amount = input("Alleged Debt Amount: $").strip()
        
        print("\n⏳ Generating debt validation request...")
        result = await executor.generate_document(
            6,
            {'AMOUNT': amount},
            client_id="quickstart_user"
        )
    
    elif choice == "6":
        # Custom Prompt
        print("CUSTOM PROMPT")
        print("-" * 40)
        prompt_num = int(input("Prompt Number (1-1000): ").strip())
        
        print("\nEnter parameters (press Enter when done):")
        parameters = {}
        while True:
            key = input("  Parameter name (or Enter to finish): ").strip()
            if not key:
                break
            value = input(f"  Value for {key}: ").strip()
            parameters[key] = value
        
        print(f"\n⏳ Generating document with prompt #{prompt_num}...")
        result = await executor.generate_document(
            prompt_num,
            parameters,
            client_id="quickstart_user"
        )
    
    else:
        print("❌ Invalid choice")
        return
    
    # Display results
    print()
    print("="*80)
    if result['success']:
        print("✅ DOCUMENT GENERATED SUCCESSFULLY")
        print("="*80)
        print()
        print(f"Document ID:      {result['document_id']}")
        print(f"Category:         {result['category']}")
        print(f"Quality Score:    {result['quality_score']:.2f}/1.0")
        print(f"Processing Time:  {result['processing_time']:.2f} seconds")
        print(f"Tokens Used:      {result['tokens_used']}")
        print(f"AI Provider:      {result['model']}")
        print()
        print("-"*80)
        print("GENERATED DOCUMENT:")
        print("-"*80)
        print()
        print(result['content'])
        print()
        print("-"*80)
        print(f"\n💾 Document saved to database (ID: {result['document_id']})")
        print(f"📂 Database: C:\\EQ12\\data\\legal_documents.db")
    else:
        print("❌ DOCUMENT GENERATION FAILED")
        print("="*80)
        print()
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    print()
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
