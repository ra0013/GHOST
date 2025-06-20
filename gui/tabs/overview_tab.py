#!/usr/bin/env python3
"""
GHOST Evidence Analysis - Overview Tab
Displays executive summary and evidence statistics
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Dict, Any, Optional

class OverviewTab:
    """Evidence overview and executive summary tab"""
    
    def __init__(self, parent):
        self.parent = parent
        
        # Create main frame
        self.frame = ttk.Frame(parent, padding="20")
        
        # Evidence cards storage
        self.evidence_cards = {}
        
        # Create widgets
        self.create_widgets()
    
    def create_widgets(self):
        """Create all widgets for the overview tab"""
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Evidence Summary Cards
        self.create_evidence_cards()
        
        # Executive Summary
        self.create_executive_summary()
    
    def create_evidence_cards(self):
        """Create evidence summary cards"""
        cards_frame = ttk.Frame(self.frame)
        cards_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        card_data = [
            ("Messages", "0", "💬"),
            ("Calls", "0", "📞"), 
            ("Photos", "0", "📷"),
            ("Videos", "0", "🎥"),
            ("Locations", "0", "📍"),
            ("Alerts", "0", "⚠️")
        ]
        
        for i, (title, value, icon) in enumerate(card_data):
            card = self.create_evidence_card(cards_frame, title, value, icon)
            card.grid(row=0, column=i, padx=5, sticky="ew")
            self.evidence_cards[title] = card
            cards_frame.grid_columnconfigure(i, weight=1)
    
    def create_evidence_card(self, parent, title: str, value: str, icon: str):
        """Create an individual evidence card"""
        card_frame = ttk.LabelFrame(parent, text=f"{icon} {title}")
        
        # Value label
        value_label = ttk.Label(card_frame, text=value, font=('Arial', 18, 'bold'))
        value_label.pack(pady=10)
        
        # Store reference to value label for updates
        card_frame.value_label = value_label
        
        return card_frame
    
    def create_executive_summary(self):
        """Create executive summary section"""
        summary_frame = ttk.LabelFrame(self.frame, text="Executive Summary")
        summary_frame.grid(row=1, column=0, sticky="nsew")
        summary_frame.grid_rowconfigure(0, weight=1)
        summary_frame.grid_columnconfigure(0, weight=1)
        
        self.executive_summary_text = scrolledtext.ScrolledText(
            summary_frame, 
            font=('Arial', 10),
            wrap='word'
        )
        self.executive_summary_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Add initial message
        self.show_no_analysis_message()
    
    def show_no_analysis_message(self):
        """Show message when no analysis has been performed"""
        message = """GHOST EVIDENCE ANALYSIS - OVERVIEW
═══════════════════════════════════════

No analysis performed yet.

To begin:
1. Go to the Case Setup tab
2. Enter case information
3. Select an extraction path (ZIP file or directory)
4. Click "Start Evidence Analysis"

The overview will display:
• Evidence type counts and statistics
• Priority assessment and risk level
• Key findings and immediate actions
• Investigation recommendations
• Timeline of discovered evidence

For best results:
• Use mobile device extractions (iOS/Android)
• Ensure extraction contains database files
• Allow sufficient time for comprehensive analysis
"""
        
        self.executive_summary_text.delete("1.0", tk.END)
        self.executive_summary_text.insert("1.0", message)
    
    def update_with_results(self, results: Dict[str, Any]):
        """Update overview with analysis results"""
        if not results:
            return
        
        # Update evidence cards
        self.update_evidence_cards(results)
        
        # Update executive summary
        self.update_executive_summary(results)
    
    def update_evidence_cards(self, results: Dict[str, Any]):
        """Update evidence summary cards"""
        evidence_summary = results.get('evidence_summary', {})
        
        # Communications data
        communications = evidence_summary.get('communications', {})
        self.update_card_value("Messages", communications.get('messages', 0))
        self.update_card_value("Calls", communications.get('calls', 0))
        
        # Multimedia data
        multimedia = evidence_summary.get('multimedia', {})
        self.update_card_value("Photos", multimedia.get('photos', 0))
        self.update_card_value("Videos", multimedia.get('videos', 0))
        
        # Location data
        digital_activity = evidence_summary.get('digital_activity', {})
        self.update_card_value("Locations", digital_activity.get('location_points', 0))
        
        # Calculate alerts from communication analysis
        comm_intel = results.get('communication_intelligence', {})
        msg_analysis = comm_intel.get('message_analysis', {})
        keyword_mentions = msg_analysis.get('keyword_mentions', {})
        alerts = sum(len(mentions) for mentions in keyword_mentions.values())
        self.update_card_value("Alerts", alerts)
    
    def update_card_value(self, card_name: str, value: int):
        """Update evidence card value"""
        if card_name in self.evidence_cards:
            card = self.evidence_cards[card_name]
            card.value_label.config(text=str(value))
            
            # Add color coding based on value
            if value > 0:
                card.value_label.config(foreground='green')
            else:
                card.value_label.config(foreground='gray')
    
    def update_executive_summary(self, results: Dict[str, Any]):
        """Update executive summary display"""
        self.executive_summary_text.delete("1.0", tk.END)
        
        # Get analysis components
        case_info = results.get('case_information', {})
        exec_summary = results.get('executive_summary', {})
        evidence_summary = results.get('evidence_summary', {})
        comm_intel = results.get('communication_intelligence', {})
        investigative_leads = results.get('investigative_leads', [])
        
        # Build summary text
        summary_text = self.build_executive_summary_text(
            case_info, exec_summary, evidence_summary, comm_intel, investigative_leads
        )
        
        self.executive_summary_text.insert("1.0", summary_text)
    
    def build_executive_summary_text(self, case_info: Dict, exec_summary: Dict, 
                                   evidence_summary: Dict, comm_intel: Dict, 
                                   investigative_leads: list) -> str:
        """Build executive summary text"""
        
        summary = f"""GHOST EVIDENCE ANALYSIS - EXECUTIVE SUMMARY
═══════════════════════════════════════════════════

CASE INFORMATION:
Case: {case_info.get('case_name', 'Unknown')}
Examiner: {case_info.get('examiner', 'Unknown')}
Analysis Date: {case_info.get('analysis_date', 'Unknown')}
Source: {case_info.get('source_path', 'Unknown')}

PRIORITY ASSESSMENT:
Level: {exec_summary.get('priority_level', 'Unknown')}
Reason: {exec_summary.get('priority_reason', 'No assessment available')}

EVIDENCE SUMMARY:
"""
        
        # Communications
        communications = evidence_summary.get('communications', {})
        summary += f"💬 Communications:\n"
        summary += f"   • Messages: {communications.get('messages', 0)}\n"
        summary += f"   • Calls: {communications.get('calls', 0)}\n"
        summary += f"   • Contacts: {communications.get('contacts', 0)}\n"
        
        # Multimedia
        multimedia = evidence_summary.get('multimedia', {})
        summary += f"\n📷 Multimedia:\n"
        summary += f"   • Photos: {multimedia.get('photos', 0)}\n"
        summary += f"   • Videos: {multimedia.get('videos', 0)}\n"
        
        # Digital Activity
        digital_activity = evidence_summary.get('digital_activity', {})
        summary += f"\n📱 Digital Activity:\n"
        summary += f"   • Browser Records: {digital_activity.get('browser_records', 0)}\n"
        summary += f"   • Location Points: {digital_activity.get('location_points', 0)}\n"
        summary += f"   • App Data: {digital_activity.get('app_data', 0)} apps\n"
        summary += f"   • Databases: {digital_activity.get('databases', 0)}\n"
        
        # Communication Intelligence
        if comm_intel:
            summary += f"\nCOMMUNICATION INTELLIGENCE:\n"
            
            msg_analysis = comm_intel.get('message_analysis', {})
            if msg_analysis:
                summary += f"📝 Message Analysis:\n"
                summary += f"   • Total Messages: {msg_analysis.get('message_count', 0)}\n"
                summary += f"   • Unique Contacts: {msg_analysis.get('unique_contacts', 0)}\n"
                
                keyword_mentions = msg_analysis.get('keyword_mentions', {})
                if keyword_mentions:
                    summary += f"   • Keywords Found: {len(keyword_mentions)} types\n"
                    for keyword, mentions in list(keyword_mentions.items())[:3]:
                        summary += f"     - '{keyword}': {len(mentions)} mentions\n"
                
                top_contacts = msg_analysis.get('top_contacts', [])
                if top_contacts:
                    summary += f"   • Top Contacts:\n"
                    for contact, count in top_contacts[:3]:
                        summary += f"     - {contact}: {count} messages\n"
            
            call_analysis = comm_intel.get('call_analysis', {})
            if call_analysis:
                summary += f"\n📞 Call Analysis:\n"
                summary += f"   • Total Calls: {call_analysis.get('call_count', 0)}\n"
                summary += f"   • Unique Numbers: {call_analysis.get('unique_numbers', 0)}\n"
                duration_hours = call_analysis.get('total_duration_minutes', 0) / 60
                summary += f"   • Total Duration: {duration_hours:.1f} hours\n"
        
        # Investigative Leads
        if investigative_leads:
            summary += f"\nINVESTIGATIVE LEADS:\n"
            for i, lead in enumerate(investigative_leads[:5], 1):
                priority = lead.get('priority', 'Unknown')
                lead_type = lead.get('type', 'Unknown')
                description = lead.get('description', 'No description')
                summary += f"{i}. [{priority}] {lead_type}\n"
                summary += f"   {description}\n"
        
        # Key Statistics
        key_stats = exec_summary.get('key_statistics', {})
        if key_stats:
            summary += f"\nKEY STATISTICS:\n"
            summary += f"• Total Communications: {key_stats.get('total_communications', 0)}\n"
            summary += f"• Unique Contacts: {key_stats.get('unique_contacts', 0)}\n"
            summary += f"• Investigation Keywords: {key_stats.get('investigation_keywords', 0)}\n"
            summary += f"• Multimedia Files: {key_stats.get('multimedia_files', 0)}\n"
            summary += f"• Location Points: {key_stats.get('location_points', 0)}\n"
        
        # Immediate Actions
        immediate_actions = exec_summary.get('immediate_actions', [])
        if immediate_actions:
            summary += f"\nIMMEDIATE ACTIONS:\n"
            for i, action in enumerate(immediate_actions, 1):
                summary += f"{i}. {action}\n"
        
        # App Intelligence
        app_intel = results.get('app_intelligence', {})
        if app_intel and app_intel.get('apps_found', 0) > 0:
            summary += f"\nAPP INTELLIGENCE:\n"
            summary += f"• Apps Found: {app_intel.get('apps_found', 0)}\n"
            app_summary = app_intel.get('app_summary', {})
            for app_name, app_info in list(app_summary.items())[:3]:
                priority = app_info.get('investigation_priority', 'Unknown')
                files = app_info.get('files_discovered', 0)
                summary += f"• {app_name}: {files} files ({priority} priority)\n"
        
        # Add analysis metadata
        summary += f"\nANALYSIS METADATA:\n"
        summary += f"• Tool Version: {case_info.get('tool_version', 'Unknown')}\n"
        summary += f"• Source Type: {case_info.get('source_type', 'Unknown')}\n"
        
        # Add recommendations footer
        summary += f"\n" + "=" * 50 + "\n"
        summary += "NEXT STEPS:\n"
        summary += "1. Review detailed findings in other tabs\n"
        summary += "2. Export data for further analysis\n"
        summary += "3. Generate formal reports\n"
        summary += "4. Coordinate with specialized units if needed\n"
        
        return summary
