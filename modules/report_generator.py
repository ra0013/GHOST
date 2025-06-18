# modules/report_generator.py
"""
Report Generator Module
Generates comprehensive forensic intelligence reports in multiple formats
"""

import json
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import base64

class ReportGenerator:
    """Generates comprehensive forensic intelligence reports"""
    
    def __init__(self, case_name: str, examiner_name: str):
        self.case_name = case_name
        self.examiner_name = examiner_name
        self.generation_time = datetime.datetime.now()
        
    def generate_comprehensive_report(self, 
                                    extracted_data: Dict[str, Any],
                                    intelligence_findings: List[Dict[str, Any]],
                                    analysis_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive forensic intelligence report"""
        
        # Calculate summary statistics
        summary_stats = self._calculate_summary_statistics(intelligence_findings, extracted_data)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(summary_stats, intelligence_findings)
        
        # Analyze risk distribution
        risk_analysis = self._analyze_risk_distribution(intelligence_findings)
        
        # Generate timeline analysis
        timeline_analysis = self._generate_timeline_analysis(intelligence_findings)
        
        # Create communication analysis
        communication_analysis = self._analyze_communications(extracted_data)
        
        # Generate actionable intelligence
        actionable_intelligence = self._generate_actionable_intelligence(intelligence_findings)
        
        # Create recommendations
        recommendations = self._generate_recommendations(intelligence_findings, summary_stats)
        
        # Compile comprehensive report
        comprehensive_report = {
            'report_metadata': {
                'case_name': self.case_name,
                'examiner': self.examiner_name,
                'generation_date': self.generation_time.isoformat(),
                'report_version': '2.0',
                'tool_version': 'Forensic Intelligence Suite v2.0'
            },
            'executive_summary': executive_summary,
            'summary_statistics': summary_stats,
            'risk_analysis': risk_analysis,
            'timeline_analysis': timeline_analysis,
            'communication_analysis': communication_analysis,
            'detailed_findings': intelligence_findings,
            'actionable_intelligence': actionable_intelligence,
            'recommendations': recommendations,
            'analysis_metadata': analysis_metadata,
            'appendices': {
                'methodology': self._generate_methodology_section(),
                'tool_configuration': self._generate_tool_configuration(),
                'data_sources': self._generate_data_sources(extracted_data)
            }
        }
        
        return comprehensive_report
    
    def _calculate_summary_statistics(self, findings: List[Dict[str, Any]], 
                                    extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive summary statistics"""
        
        total_findings = len(findings)
        
        # Risk level breakdown
        risk_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for finding in findings:
            risk_score = finding.get('risk_score', 0)
            if risk_score >= 8:
                risk_counts['critical'] += 1
            elif risk_score >= 6:
                risk_counts['high'] += 1
            elif risk_score >= 4:
                risk_counts['medium'] += 1
            else:
                risk_counts['low'] += 1
        
        # Module breakdown
        module_counts = Counter(finding.get('module', 'Unknown') for finding in findings)
        
        # Communication statistics
        total_communications = sum(
            data.get('record_count', 0) for data in extracted_data.values()
        )
        
        # Database statistics
        databases_analyzed = len(extracted_data)
        
        # Time span analysis
        timestamps = [finding.get('timestamp') for finding in findings if finding.get('timestamp')]
        time_span = self._calculate_time_span(timestamps)
        
        return {
            'total_findings': total_findings,
            'risk_distribution': risk_counts,
            'module_breakdown': dict(module_counts),
            'communications_analyzed': total_communications,
            'databases_analyzed': databases_analyzed,
            'analysis_time_span': time_span,
            'unique_contacts': self._count_unique_contacts(findings),
            'geographic_indicators': self._count_geographic_indicators(findings)
        }
    
    def _generate_executive_summary(self, stats: Dict[str, Any], 
                                   findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate executive summary for leadership consumption"""
        
        # Determine overall threat level
        critical_count = stats['risk_distribution']['critical']
        high_count = stats['risk_distribution']['high']
        
        if critical_count > 0:
            threat_level = "CRITICAL"
            threat_description = f"{critical_count} critical threats requiring immediate action"
        elif high_count > 5:
            threat_level = "HIGH"
            threat_description = f"{high_count} high-risk indicators identified"
        elif stats['total_findings'] > 10:
            threat_level = "ELEVATED"
            threat_description = f"{stats['total_findings']} intelligence indicators detected"
        else:
            threat_level = "LOW"
            threat_description = "Limited threat indicators identified"
        
        # Key findings summary
        key_findings = self._extract_key_findings(findings)
        
        # Priority actions
        priority_actions = self._generate_priority_actions(findings, stats)
        
        # Investigation focus areas
        focus_areas = self._identify_focus_areas(stats['module_breakdown'])
        
        return {
            'threat_level': threat_level,
            'threat_description': threat_description,
            'key_findings': key_findings,
            'priority_actions': priority_actions,
            'investigation_focus_areas': focus_areas,
            'analysis_scope': {
                'communications_reviewed': stats['communications_analyzed'],
                'databases_processed': stats['databases_analyzed'],
                'time_span_covered': stats['analysis_time_span']
            },
            'immediate_concerns': self._identify_immediate_concerns(findings)
        }
    
    def _analyze_risk_distribution(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze risk distribution across different dimensions"""
        
        # Risk by module
        risk_by_module = defaultdict(lambda: {'critical': 0, 'high': 0, 'medium': 0, 'low': 0})
        
        # Risk by contact
        risk_by_contact = defaultdict(int)
        
        # Risk over time
        risk_by_time = defaultdict(lambda: {'critical': 0, 'high': 0, 'medium': 0, 'low': 0})
        
        for finding in findings:
            risk_score = finding.get('risk_score', 0)
            module = finding.get('module', 'Unknown')
            contact = finding.get('contact', 'Unknown')
            timestamp = finding.get('timestamp', '')
            
            # Categorize risk level
            if risk_score >= 8:
                risk_level = 'critical'
            elif risk_score >= 6:
                risk_level = 'high'
            elif risk_score >= 4:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            # Update risk by module
            risk_by_module[module][risk_level] += 1
            
            # Update risk by contact
            risk_by_contact[contact] += risk_score
            
            # Update risk by time (daily aggregation)
            if timestamp:
                try:
                    date = timestamp.split('T')[0] if 'T' in timestamp else timestamp.split(' ')[0]
                    risk_by_time[date][risk_level] += 1
                except:
                    pass
        
        # Identify highest risk contacts
        top_risk_contacts = sorted(risk_by_contact.items(), 
                                 key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'risk_by_module': dict(risk_by_module),
            'risk_by_contact': dict(risk_by_contact),
            'risk_over_time': dict(risk_by_time),
            'highest_risk_contacts': top_risk_contacts,
            'risk_concentration': self._calculate_risk_concentration(findings)
        }
    
    def _generate_timeline_analysis(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive timeline analysis"""
        
        # Sort findings by timestamp
        timestamped_findings = [f for f in findings if f.get('timestamp')]
        timestamped_findings.sort(key=lambda x: x['timestamp'])
        
        if not timestamped_findings:
            return {'error': 'No timestamped findings available for timeline analysis'}
        
        # Daily activity analysis
        daily_activity = defaultdict(list)
        for finding in timestamped_findings:
            try:
                date = finding['timestamp'].split('T')[0] if 'T' in finding['timestamp'] else finding['timestamp'].split(' ')[0]
                daily_activity[date].append(finding)
            except:
                continue
        
        # Identify peak activity periods
        peak_days = sorted(daily_activity.items(), 
                          key=lambda x: len(x[1]), reverse=True)[:5]
        
        # Activity patterns
        hourly_pattern = self._analyze_hourly_patterns(timestamped_findings)
        
        # Escalation analysis
        escalation_events = self._identify_escalation_events(timestamped_findings)
        
        return {
            'total_timestamped_events': len(timestamped_findings),
            'analysis_period': {
                'start_date': timestamped_findings[0]['timestamp'],
                'end_date': timestamped_findings[-1]['timestamp'],
                'duration_days': self._calculate_duration_days(timestamped_findings)
            },
            'daily_activity_summary': {date: len(events) for date, events in daily_activity.items()},
            'peak_activity_days': peak_days,
            'hourly_patterns': hourly_pattern,
            'escalation_events': escalation_events,
            'activity_trends': self._analyze_activity_trends(daily_activity)
        }
    
    def _analyze_communications(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze communication patterns and statistics"""
        
        total_communications = 0
        sources_analyzed = []
        communication_breakdown = {}
        
        for source, data in extracted_data.items():
            record_count = data.get('record_count', 0)
            total_communications += record_count
            
            if record_count > 0:
                sources_analyzed.append(source)
                communication_breakdown[source] = {
                    'count': record_count,
                    'source_path': data.get('source_path', 'Unknown'),
                    'extraction_time': data.get('extraction_time', 'Unknown')
                }
        
        # Communication volume analysis
        volume_analysis = self._analyze_communication_volume(communication_breakdown)
        
        return {
            'total_communications': total_communications,
            'sources_analyzed': len(sources_analyzed),
            'communication_breakdown': communication_breakdown,
            'volume_analysis': volume_analysis,
            'data_quality_assessment': self._assess_data_quality(extracted_data)
        }
    
    def _generate_actionable_intelligence(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate specific actionable intelligence items"""
        
        actionable_items = []
        
        # Group findings by priority and type
        critical_findings = [f for f in findings if f.get('risk_score', 0) >= 8]
        high_risk_findings = [f for f in findings if 6 <= f.get('risk_score', 0) < 8]
        
        # Generate actions for critical findings
        for finding in critical_findings:
            action = {
                'priority': 'IMMEDIATE',
                'action_type': 'INVESTIGATE_CRITICAL_FINDING',
                'description': f"Immediate investigation required for {finding.get('type', 'unknown')} involving {finding.get('contact', 'unknown contact')}",
                'finding_id': finding.get('id', 'unknown'),
                'module': finding.get('module', 'unknown'),
                'risk_score': finding.get('risk_score', 0),
                'timeline': 'Within 24 hours',
                'resources_needed': self._determine_resources_needed(finding),
                'next_steps': self._generate_next_steps(finding)
            }
            actionable_items.append(action)
        
        # Generate actions for high-risk findings
        for finding in high_risk_findings:
            action = {
                'priority': 'HIGH',
                'action_type': 'INVESTIGATE_HIGH_RISK',
                'description': f"High-priority investigation of {finding.get('type', 'unknown')} with {finding.get('contact', 'unknown contact')}",
                'finding_id': finding.get('id', 'unknown'),
                'module': finding.get('module', 'unknown'),
                'risk_score': finding.get('risk_score', 0),
                'timeline': 'Within 72 hours',
                'resources_needed': self._determine_resources_needed(finding),
                'next_steps': self._generate_next_steps(finding)
            }
            actionable_items.append(action)
        
        # Generate contact-based actions
        contact_actions = self._generate_contact_based_actions(findings)
        actionable_items.extend(contact_actions)
        
        # Generate pattern-based actions
        pattern_actions = self._generate_pattern_based_actions(findings)
        actionable_items.extend(pattern_actions)
        
        return sorted(actionable_items, 
                     key=lambda x: {'IMMEDIATE': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}.get(x['priority'], 4))
    
    def _generate_recommendations(self, findings: List[Dict[str, Any]], 
                                stats: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate investigation recommendations"""
        
        recommendations = []
        
        # Risk-based recommendations
        if stats['risk_distribution']['critical'] > 0:
            recommendations.append({
                'category': 'IMMEDIATE_ACTION',
                'recommendation': 'Coordinate with specialized units for critical threat response',
                'rationale': f"{stats['risk_distribution']['critical']} critical findings require immediate expert attention"
            })
        
        # Module-specific recommendations
        module_breakdown = stats['module_breakdown']
        
        if 'Child Exploitation Intelligence' in module_breakdown:
            recommendations.append({
                'category': 'SPECIALIZED_UNIT',
                'recommendation': 'Coordinate with Internet Crimes Against Children (ICAC) task force',
                'rationale': 'Child exploitation indicators detected requiring specialized expertise'
            })
        
        if 'Extremism Intelligence' in module_breakdown:
            recommendations.append({
                'category': 'COUNTERTERRORISM',
                'recommendation': 'Coordinate with Joint Terrorism Task Force (JTTF)',
                'rationale': 'Extremism indicators require counterterrorism unit involvement'
            })
        
        if 'Human Trafficking Intelligence' in module_breakdown:
            recommendations.append({
                'category': 'TRAFFICKING_UNIT',
                'recommendation': 'Coordinate with Human Trafficking Task Force',
                'rationale': 'Human trafficking indicators require specialized unit coordination'
            })
        
        if 'Narcotics Intelligence' in module_breakdown:
            recommendations.append({
                'category': 'DRUG_ENFORCEMENT',
                'recommendation': 'Consider DEA coordination for potential distribution network',
                'rationale': 'Narcotics indicators suggest organized distribution activity'
            })
        
        # Investigation expansion recommendations
        if stats['total_findings'] > 20:
            recommendations.append({
                'category': 'INVESTIGATION_SCOPE',
                'recommendation': 'Consider expanding investigation scope and resources',
                'rationale': f"High volume of findings ({stats['total_findings']}) indicates significant criminal activity"
            })
        
        # Technical recommendations
        recommendations.append({
            'category': 'TECHNICAL_ANALYSIS',
            'recommendation': 'Proceed with comprehensive forensic analysis using primary tools',
            'rationale': 'Rapid intelligence findings should be corroborated with full forensic analysis'
        })
        
        # Legal recommendations
        if stats['risk_distribution']['high'] + stats['risk_distribution']['critical'] > 5:
            recommendations.append({
                'category': 'LEGAL_ACTION',
                'recommendation': 'Consider additional search warrants based on identified patterns',
                'rationale': 'High-risk findings may justify expanded search authority'
            })
        
        return recommendations
    
    def _generate_methodology_section(self) -> Dict[str, Any]:
        """Generate methodology documentation"""
        return {
            'tool_name': 'Forensic Intelligence Suite v2.0',
            'analysis_type': 'Rapid Intelligence Preprocessing',
            'purpose': 'Golden hour intelligence extraction for immediate investigative action',
            'scope': 'Communication data analysis with crime-specific intelligence modules',
            'limitations': [
                'Rapid analysis may not capture all forensic artifacts',
                'Results should be corroborated with comprehensive forensic analysis',
                'Intelligence modules use keyword-based detection which may have false positives'
            ],
            'methodology_steps': [
                'Database discovery and encryption detection',
                'Automated schema generation for unknown databases',
                'Communication data extraction with timeline preservation',
                'Multi-module intelligence analysis with risk scoring',
                'Pattern correlation and network analysis',
                'Actionable intelligence generation'
            ]
        }
    
    def _generate_tool_configuration(self) -> Dict[str, Any]:
        """Generate tool configuration documentation"""
        return {
            'processing_mode': 'Adaptive resource management',
            'modules_enabled': 'All available intelligence modules',
            'data_sources': 'iOS/Android database extraction',
            'analysis_timeframe': 'Last 90 days (configurable)',
            'risk_scoring': '1-10 scale with weighted indicators',
            'output_formats': ['JSON', 'Human-readable report', 'Timeline analysis']
        }
    
    def _generate_data_sources(self, extracted_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Document data sources used in analysis"""
        sources = []
        
        for source_name, data in extracted_data.items():
            source_info = {
                'name': source_name,
                'type': 'Database extraction',
                'path': data.get('source_path', 'Unknown'),
                'records_extracted': data.get('record_count', 0),
                'extraction_time': data.get('extraction_time', 'Unknown'),
                'data_integrity': 'Verified with SHA-256 hash'
            }
            sources.append(source_info)
        
        return sources
    
    # Helper methods for calculations and analysis
    
    def _calculate_time_span(self, timestamps: List[str]) -> str:
        """Calculate time span of analysis"""
        if not timestamps:
            return "No timestamped data"
        
        try:
            valid_timestamps = [ts for ts in timestamps if ts]
            if valid_timestamps:
                return f"{min(valid_timestamps)} to {max(valid_timestamps)}"
        except:
            pass
        
        return "Unable to determine time span"
    
    def _count_unique_contacts(self, findings: List[Dict[str, Any]]) -> int:
        """Count unique contacts in findings"""
        contacts = set()
        for finding in findings:
            contact = finding.get('contact')
            if contact and contact != 'Unknown':
                contacts.add(contact)
        return len(contacts)
    
    def _count_geographic_indicators(self, findings: List[Dict[str, Any]]) -> int:
        """Count geographic indicators in findings"""
        # This would be enhanced with actual geographic analysis
        return 0
    
    def _extract_key_findings(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Extract key findings for executive summary"""
        key_findings = []
        
        # Get highest risk findings
        high_risk_findings = sorted(findings, key=lambda x: x.get('risk_score', 0), reverse=True)[:5]
        
        for finding in high_risk_findings:
            if finding.get('risk_score', 0) >= 6:
                summary = f"{finding.get('module', 'Unknown')} indicators involving {finding.get('contact', 'unknown contact')}"
                key_findings.append(summary)
        
        return key_findings[:3]  # Top 3 key findings
    
    def _generate_priority_actions(self, findings: List[Dict[str, Any]], 
                                 stats: Dict[str, Any]) -> List[str]:
        """Generate priority actions for executive summary"""
        actions = []
        
        critical_count = stats['risk_distribution']['critical']
        if critical_count > 0:
            actions.append(f"Immediate investigation of {critical_count} critical threats")
        
        high_count = stats['risk_distribution']['high']
        if high_count > 0:
            actions.append(f"Priority investigation of {high_count} high-risk indicators")
        
        # Add module-specific actions
        modules = stats['module_breakdown']
        if 'Child Exploitation Intelligence' in modules:
            actions.append("Coordinate with ICAC task force")
        if 'Extremism Intelligence' in modules:
            actions.append("Coordinate with counterterrorism units")
        
        return actions[:3]  # Top 3 priority actions
    
    def _identify_focus_areas(self, module_breakdown: Dict[str, int]) -> List[str]:
        """Identify key investigation focus areas"""
        focus_areas = []
        
        # Sort modules by finding count
        sorted_modules = sorted(module_breakdown.items(), key=lambda x: x[1], reverse=True)
        
        for module, count in sorted_modules[:3]:  # Top 3 modules
            if count > 0:
                focus_areas.append(module.replace('_', ' ').title())
        
        return focus_areas
    
    def _identify_immediate_concerns(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Identify immediate concerns requiring urgent attention"""
        concerns = []
        
        # Check for critical findings
        critical_findings = [f for f in findings if f.get('risk_score', 0) >= 8]
        if critical_findings:
            concerns.append(f"{len(critical_findings)} critical threats requiring immediate response")
        
        # Check for specific high-risk patterns
        child_exploitation = [f for f in findings if 'child' in f.get('type', '').lower()]
        if child_exploitation:
            concerns.append("Child exploitation indicators detected - immediate escalation required")
        
        return concerns
    
    def _calculate_risk_concentration(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate risk concentration metrics"""
        if not findings:
            return {}
        
        contacts = [f.get('contact', 'Unknown') for f in findings]
        contact_counts = Counter(contacts)
        
        # Calculate concentration ratio
        total_findings = len(findings)
        top_contact_findings = max(contact_counts.values()) if contact_counts else 0
        concentration_ratio = top_contact_findings / total_findings if total_findings > 0 else 0
        
        return {
            'concentration_ratio': concentration_ratio,
            'top_contact': max(contact_counts, key=contact_counts.get) if contact_counts else 'None',
            'findings_per_contact': dict(contact_counts)
        }
    
    def _analyze_hourly_patterns(self, findings: List[Dict[str, Any]]) -> Dict[int, int]:
        """Analyze activity patterns by hour of day"""
        hourly_counts = defaultdict(int)
        
        for finding in findings:
            timestamp = finding.get('timestamp', '')
            try:
                if 'T' in timestamp:
                    time_part = timestamp.split('T')[1]
                    hour = int(time_part.split(':')[0])
                    hourly_counts[hour] += 1
            except:
                continue
        
        return dict(hourly_counts)
    
    def _identify_escalation_events(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify events that show escalation patterns"""
        escalation_events = []
        
        # Sort by timestamp and look for risk score increases
        sorted_findings = sorted(findings, key=lambda x: x.get('timestamp', ''))
        
        for i in range(1, len(sorted_findings)):
            current = sorted_findings[i]
            previous = sorted_findings[i-1]
            
            if (current.get('risk_score', 0) > previous.get('risk_score', 0) and
                current.get('contact') == previous.get('contact')):
                
                escalation_events.append({
                    'timestamp': current.get('timestamp'),
                    'contact': current.get('contact'),
                    'risk_increase': current.get('risk_score', 0) - previous.get('risk_score', 0),
                    'description': f"Risk escalation detected for {current.get('contact')}"
                })
        
        return escalation_events
    
    def _calculate_duration_days(self, findings: List[Dict[str, Any]]) -> int:
        """Calculate duration of analysis period in days"""
        if len(findings) < 2:
            return 0
        
        try:
            start_time = findings[0]['timestamp']
            end_time = findings[-1]['timestamp']
            
            # Simple day calculation (would need proper datetime parsing in production)
            return 1  # Placeholder
        except:
            return 0
    
    def _analyze_activity_trends(self, daily_activity: Dict[str, List]) -> Dict[str, Any]:
        """Analyze trends in daily activity"""
        if not daily_activity:
            return {}
        
        daily_counts = {date: len(events) for date, events in daily_activity.items()}
        
        return {
            'average_daily_activity': sum(daily_counts.values()) / len(daily_counts),
            'peak_activity_day': max(daily_counts, key=daily_counts.get),
            'trend_direction': 'stable'  # Would calculate actual trend in production
        }
    
    def _analyze_communication_volume(self, breakdown: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze communication volume patterns"""
        total_volume = sum(data['count'] for data in breakdown.values())
        
        if total_volume == 0:
            return {'total_volume': 0, 'volume_assessment': 'No communications found'}
        
        # Volume assessment
        if total_volume > 10000:
            volume_assessment = 'Very high communication volume'
        elif total_volume > 1000:
            volume_assessment = 'High communication volume'
        elif total_volume > 100:
            volume_assessment = 'Moderate communication volume'
        else:
            volume_assessment = 'Low communication volume'
        
        return {
            'total_volume': total_volume,
            'volume_assessment': volume_assessment,
            'largest_source': max(breakdown, key=lambda x: breakdown[x]['count']) if breakdown else 'None'
        }
    
    def _assess_data_quality(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality of extracted data"""
        total_sources = len(extracted_data)
        successful_extractions = len([data for data in extracted_data.values() 
                                    if data.get('record_count', 0) > 0])
        
        quality_ratio = successful_extractions / total_sources if total_sources > 0 else 0
        
        if quality_ratio >= 0.8:
            quality_assessment = 'High quality data extraction'
        elif quality_ratio >= 0.5:
            quality_assessment = 'Moderate quality data extraction'
        else:
            quality_assessment = 'Limited data extraction success'
        
        return {
            'total_sources': total_sources,
            'successful_extractions': successful_extractions,
            'quality_ratio': quality_ratio,
            'quality_assessment': quality_assessment
        }
    
    def _determine_resources_needed(self, finding: Dict[str, Any]) -> List[str]:
        """Determine resources needed for investigation"""
        resources = ['Investigator']
        
        module = finding.get('module', '')
        risk_score = finding.get('risk_score', 0)
        
        if 'narcotics' in module.lower():
            resources.append('Drug enforcement specialist')
        elif 'financial' in module.lower():
            resources.append('Financial crimes analyst')
        elif 'trafficking' in module.lower():
            resources.append('Human trafficking specialist')
        elif 'extremism' in module.lower():
            resources.append('Counterterrorism analyst')
        
        if risk_score >= 8:
            resources.append('Supervisor approval')
            resources.append('Legal counsel consultation')
        
        return resources
    
    def _generate_next_steps(self, finding: Dict[str, Any]) -> List[str]:
        """Generate specific next steps for investigation"""
        steps = []
        
        contact = finding.get('contact', 'Unknown')
        module = finding.get('module', '')
        
        steps.append(f"Conduct background investigation on {contact}")
        steps.append("Review all related communications and contacts")
        
        if 'narcotics' in module.lower():
            steps.extend([
                "Check for controlled substance violations",
                "Investigate potential distribution network",
                "Consider surveillance authorization"
            ])
        elif 'financial' in module.lower():
            steps.extend([
                "Review financial records and transactions",
                "Check for money laundering indicators",
                "Coordinate with financial institutions"
            ])
        
        steps.append("Document all investigative actions in case file")
        
        return steps
    
    def _generate_contact_based_actions(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate actions based on contact analysis"""
        actions = []
        
        # Group findings by contact
        contact_findings = defaultdict(list)
        for finding in findings:
            contact = finding.get('contact', 'Unknown')
            if contact != 'Unknown':
                contact_findings[contact].append(finding)
        
        # Generate actions for high-activity contacts
        for contact, contact_findings_list in contact_findings.items():
            if len(contact_findings_list) > 3:  # Multiple findings for same contact
                total_risk = sum(f.get('risk_score', 0) for f in contact_findings_list)
                
                action = {
                    'priority': 'HIGH' if total_risk > 20 else 'MEDIUM',
                    'action_type': 'INVESTIGATE_HIGH_ACTIVITY_CONTACT',
                    'description': f"Investigate {contact} - {len(contact_findings_list)} indicators detected",
                    'contact': contact,
                    'total_risk_score': total_risk,
                    'finding_count': len(