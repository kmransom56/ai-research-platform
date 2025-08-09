"""
GenAI Stack Network Query Agent
Enables natural language queries about network infrastructure
Integrates Neo4j knowledge graph with GenAI Stack for intelligent responses
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import asyncio
from neo4j_network_schema import NetworkKnowledgeGraph

class NetworkQueryAgent:
    """
    Natural language interface for network queries
    Integrates with GenAI Stack and Neo4j knowledge graph
    """
    
    def __init__(self, 
                 neo4j_uri: str = "neo4j://localhost:7687",
                 genai_api_base: str = "http://localhost:8504"):
        self.kg = NetworkKnowledgeGraph(neo4j_uri)
        self.genai_api = genai_api_base
        self.logger = logging.getLogger("NetworkQueryAgent")
        
        # Common network query patterns and their mappings
        self.query_patterns = {
            "device_status": [
                "show devices", "list devices", "device status", "what devices",
                "how many devices", "device inventory", "equipment list"
            ],
            "health_check": [
                "network health", "system health", "overall status", "health score",
                "performance", "uptime", "availability", "operational status"
            ],
            "critical_issues": [
                "critical", "offline", "down", "failed", "problems", "issues",
                "alerts", "outages", "failures", "broken"
            ],
            "network_topology": [
                "topology", "connections", "network map", "relationships",
                "connected to", "network layout", "infrastructure"
            ],
            "location_based": [
                "in location", "at site", "restaurant", "office", "branch",
                "by region", "specific location"
            ],
            "trending": [
                "trends", "over time", "historical", "patterns", "changes",
                "improvement", "degradation", "timeline"
            ]
        }

    def close(self):
        """Close connections"""
        if self.kg:
            self.kg.close()

    async def process_natural_language_query(self, question: str, 
                                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process natural language question about network infrastructure
        Returns structured response with data and natural language explanation
        """
        self.logger.info(f"🗣️ Processing query: {question}")
        
        try:
            # Analyze question to determine query type
            query_intent = self._analyze_query_intent(question)
            
            # Extract parameters from question
            parameters = self._extract_query_parameters(question, context)
            
            # Execute appropriate network query
            raw_results = await self._execute_network_query(query_intent, parameters)
            
            # Generate natural language response
            nl_response = await self._generate_natural_language_response(
                question, query_intent, raw_results
            )
            
            return {
                "question": question,
                "query_intent": query_intent,
                "parameters": parameters,
                "raw_data": raw_results,
                "natural_language_response": nl_response,
                "timestamp": datetime.now().isoformat(),
                "data_summary": self._create_data_summary(raw_results)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Query processing failed: {e}")
            return {
                "question": question,
                "error": str(e),
                "natural_language_response": f"I apologize, but I encountered an error while processing your question: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def _analyze_query_intent(self, question: str) -> str:
        """Analyze question to determine the type of network query needed"""
        question_lower = question.lower()
        
        # Score each pattern type
        pattern_scores = {}
        for pattern_type, keywords in self.query_patterns.items():
            score = sum(1 for keyword in keywords if keyword in question_lower)
            if score > 0:
                pattern_scores[pattern_type] = score
        
        if not pattern_scores:
            return "general_overview"  # Default fallback
        
        # Return the highest scoring pattern
        return max(pattern_scores, key=pattern_scores.get)

    def _extract_query_parameters(self, question: str, 
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract specific parameters from the natural language question"""
        parameters = {}
        question_lower = question.lower()
        
        # Extract location/site information
        location_keywords = ["at", "in", "for", "location", "site", "branch", "office"]
        for keyword in location_keywords:
            if keyword in question_lower:
                # Simple extraction - in real implementation would use NLP
                words = question_lower.split()
                try:
                    idx = words.index(keyword)
                    if idx + 1 < len(words):
                        parameters["location"] = words[idx + 1]
                except ValueError:
                    pass
        
        # Extract time-related parameters
        time_keywords = {
            "today": "P1D",
            "yesterday": "P1D", 
            "this week": "P7D",
            "last week": "P7D",
            "this month": "P30D",
            "last hour": "PT1H"
        }
        
        for phrase, duration in time_keywords.items():
            if phrase in question_lower:
                parameters["time_period"] = duration
                break
        
        # Extract device type or model
        device_types = ["switch", "router", "firewall", "access point", "camera", "mx", "mr", "ms"]
        for device_type in device_types:
            if device_type in question_lower:
                parameters["device_type"] = device_type
                break
        
        # Extract severity/status
        if any(word in question_lower for word in ["critical", "severe", "urgent"]):
            parameters["severity"] = "critical"
        elif any(word in question_lower for word in ["offline", "down", "failed"]):
            parameters["status"] = "offline"
        
        return parameters

    async def _execute_network_query(self, query_intent: str, 
                                    parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the appropriate network query based on intent and parameters"""
        
        if query_intent == "critical_issues":
            return {
                "critical_devices": self.kg.query_network_insights("critical_devices", parameters),
                "recent_alerts": self.kg.query_network_insights("alert_patterns", parameters)
            }
        
        elif query_intent == "health_check":
            return {
                "network_health": self.kg.query_network_insights("network_health_summary", parameters),
                "organization_overview": self.kg.query_network_insights("organization_overview", parameters)
            }
        
        elif query_intent == "device_status":
            # Custom query for device status
            with self.kg.driver.session() as session:
                query = """
                MATCH (d:Device)
                OPTIONAL MATCH (d)-[:HAS_HEALTH_METRIC]->(h:HealthMetric)
                WHERE h.timestamp IS NULL OR h.timestamp > datetime() - duration('PT1H')
                RETURN d.serial, d.model, d.name, d.status, d.network_name, d.organization_name,
                       h.uptime_score, h.performance_score, h.alert_level
                ORDER BY d.organization_name, d.network_name, d.serial
                LIMIT 50
                """
                result = session.run(query, parameters)
                devices = [record.data() for record in result]
            
            return {"devices": devices}
        
        elif query_intent == "network_topology":
            return {
                "topology": self.kg.query_network_insights("device_topology", parameters)
            }
        
        else:  # general_overview
            return {
                "organizations": self.kg.query_network_insights("organization_overview", parameters),
                "network_summary": self.kg.query_network_insights("network_health_summary", parameters),
                "critical_devices": self.kg.query_network_insights("critical_devices", parameters)[:5]
            }

    async def _generate_natural_language_response(self, question: str, 
                                                 query_intent: str, 
                                                 raw_results: Dict[str, Any]) -> str:
        """Generate natural language response using GenAI Stack"""
        
        try:
            # Prepare context for GenAI
            context = {
                "question": question,
                "query_intent": query_intent,
                "data_summary": self._create_data_summary(raw_results),
                "timestamp": datetime.now().isoformat()
            }
            
            # Create prompt for GenAI
            prompt = self._create_genai_prompt(question, query_intent, raw_results)
            
            # Call GenAI Stack API
            response = await self._call_genai_api(prompt, context)
            
            if response and "response" in response:
                return response["response"]
            else:
                # Fallback to template-based response
                return self._generate_template_response(query_intent, raw_results)
        
        except Exception as e:
            self.logger.warning(f"GenAI response generation failed, using template: {e}")
            return self._generate_template_response(query_intent, raw_results)

    def _create_genai_prompt(self, question: str, query_intent: str, 
                            raw_results: Dict[str, Any]) -> str:
        """Create prompt for GenAI Stack to generate natural language response"""
        
        data_summary = self._create_data_summary(raw_results)
        
        prompt = f"""
You are a network operations expert assistant. A user asked: "{question}"

Based on the network data analysis, here's what I found:

{json.dumps(data_summary, indent=2)}

Please provide a clear, concise, and actionable response that:
1. Directly answers the user's question
2. Highlights the most important findings
3. Provides specific recommendations if issues are found
4. Uses business-friendly language (avoid technical jargon where possible)
5. Mentions specific devices, networks, or locations when relevant

Keep the response conversational and helpful, as if you're speaking to a network administrator who needs to take action.
"""
        return prompt

    async def _call_genai_api(self, prompt: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call GenAI Stack API for natural language generation"""
        try:
            # GenAI Stack API endpoint
            endpoint = f"{self.genai_api}/generate"
            
            payload = {
                "prompt": prompt,
                "context": context,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            # Make async request
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=payload, timeout=30) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.warning(f"GenAI API returned status {response.status}")
                        return None
        
        except Exception as e:
            self.logger.warning(f"GenAI API call failed: {e}")
            return None

    def _generate_template_response(self, query_intent: str, raw_results: Dict[str, Any]) -> str:
        """Generate template-based response as fallback"""
        
        data_summary = self._create_data_summary(raw_results)
        
        if query_intent == "critical_issues":
            critical_count = data_summary.get("critical_devices_count", 0)
            if critical_count > 0:
                return f"⚠️ I found {critical_count} critical devices that need immediate attention. These devices are currently offline or experiencing severe issues. I recommend investigating these devices first to restore service."
            else:
                return "✅ Great news! I didn't find any critical device issues at this time. All systems appear to be operating normally."
        
        elif query_intent == "health_check":
            avg_health = data_summary.get("average_health_score", 0)
            total_devices = data_summary.get("total_devices", 0)
            
            if avg_health >= 90:
                status = "excellent"
                emoji = "🌟"
            elif avg_health >= 80:
                status = "good"
                emoji = "✅"
            elif avg_health >= 70:
                status = "fair"
                emoji = "⚠️"
            else:
                status = "needs attention"
                emoji = "🚨"
            
            return f"{emoji} Your network health is {status} with an overall score of {avg_health:.1f}%. I'm monitoring {total_devices} devices across your infrastructure."
        
        elif query_intent == "device_status":
            device_count = data_summary.get("total_devices", 0)
            online_count = data_summary.get("online_devices", 0)
            return f"📊 I found {device_count} devices in your network. {online_count} devices are currently online and operational."
        
        else:  # general_overview
            orgs = data_summary.get("organizations_count", 0)
            networks = data_summary.get("networks_count", 0)
            devices = data_summary.get("total_devices", 0)
            
            return f"📋 Here's your network overview: {orgs} organizations, {networks} networks, and {devices} devices. The system is monitoring all components for health and performance."

    def _create_data_summary(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary statistics from raw query results"""
        summary = {}
        
        # Process different result types
        if "critical_devices" in raw_results:
            summary["critical_devices_count"] = len(raw_results["critical_devices"])
        
        if "devices" in raw_results:
            devices = raw_results["devices"]
            summary["total_devices"] = len(devices)
            summary["online_devices"] = len([d for d in devices if d.get("status") == "online"])
            summary["offline_devices"] = len([d for d in devices if d.get("status") == "offline"])
        
        if "network_health" in raw_results:
            health_data = raw_results["network_health"]
            if health_data:
                total_health = sum(item.get("health_percentage", 0) for item in health_data)
                summary["average_health_score"] = total_health / len(health_data)
                summary["networks_count"] = len(health_data)
        
        if "organizations" in raw_results:
            summary["organizations_count"] = len(raw_results["organizations"])
        
        if "topology" in raw_results:
            summary["topology_relationships"] = len(raw_results["topology"])
        
        return summary

    # Predefined query templates for common network questions
    async def get_critical_alerts(self) -> Dict[str, Any]:
        """Get current critical alerts"""
        return await self.process_natural_language_query("What critical alerts do we have?")

    async def get_network_health(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get network health status"""
        question = f"What is the network health status{' for ' + location if location else ''}?"
        return await self.process_natural_language_query(question)

    async def get_offline_devices(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get offline devices"""
        question = f"What devices are offline{' in ' + location if location else ''}?"
        return await self.process_natural_language_query(question)

    async def get_device_inventory(self, device_type: Optional[str] = None) -> Dict[str, Any]:
        """Get device inventory"""
        question = f"Show me all {device_type + ' ' if device_type else ''}devices"
        return await self.process_natural_language_query(question)

    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return await self.process_natural_language_query("How is network performance?")

# Integration with Chat Copilot
class ChatCopilotNetworkInterface:
    """
    Interface for Chat Copilot to access network query capabilities
    Provides natural language network management through the AI platform
    """
    
    def __init__(self):
        self.query_agent = NetworkQueryAgent()
        self.logger = logging.getLogger("ChatCopilotNetworkInterface")

    async def handle_network_question(self, question: str, 
                                     user_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Handle network-related questions from Chat Copilot
        Returns natural language response suitable for chat interface
        """
        try:
            result = await self.query_agent.process_natural_language_query(question, user_context)
            
            # Format response for Chat Copilot
            response = result.get("natural_language_response", "I couldn't process that question.")
            
            # Add action buttons if critical issues found
            if "critical" in response.lower() and result.get("data_summary", {}).get("critical_devices_count", 0) > 0:
                response += "\n\n🔧 Would you like me to help you troubleshoot these critical devices?"
            
            return response
            
        except Exception as e:
            self.logger.error(f"Chat Copilot network question handling failed: {e}")
            return f"I'm sorry, I encountered an issue while checking your network: {str(e)}"

    def close(self):
        """Close connections"""
        if self.query_agent:
            self.query_agent.close()

# Example usage and testing
if __name__ == "__main__":
    async def test_network_queries():
        agent = NetworkQueryAgent()
        
        test_questions = [
            "What devices are offline?",
            "Show me network health status",
            "List all devices in the main office",
            "Are there any critical alerts?",
            "How is network performance today?",
            "What switches need attention?",
            "Show me the network topology",
            "Which locations have the most issues?"
        ]
        
        print("=== NATURAL LANGUAGE NETWORK QUERIES TEST ===")
        
        for question in test_questions:
            print(f"\n🗣️ Q: {question}")
            try:
                result = await agent.process_natural_language_query(question)
                print(f"💬 A: {result['natural_language_response']}")
                
                # Show data summary
                if result.get("data_summary"):
                    summary = result["data_summary"]
                    print(f"📊 Data: {summary}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
        
        agent.close()
        print("\n✅ Natural language query test completed!")

    # Run test
    asyncio.run(test_network_queries())