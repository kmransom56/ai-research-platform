// Network Topology & Device Inventory Queries for Neo4j
// Copy and paste these into Neo4j Browser at http://localhost:7474

// 1. COMPLETE DEVICE INVENTORY - All Meraki/Fortinet Equipment
MATCH (d:Device)
RETURN d.name as DeviceName, 
       d.model as Model, 
       d.platform as Platform,
       d.device_type as Type,
       d.status as Status,
       d.location as Location,
       d.serial as Serial,
       d.firmware_version as Firmware
ORDER BY d.platform, d.location, d.name;

// 2. NETWORK TOPOLOGY - Physical and Logical Connections
MATCH (n:Network)-[:CONTAINS]->(d:Device)
OPTIONAL MATCH (d)-[r:CONNECTED_TO]->(d2:Device)
RETURN n.name as NetworkName, 
       d.name as Device, 
       d.device_type as Type,
       collect(d2.name) as ConnectedDevices,
       d.location as Location;

// 3. HIERARCHICAL TOPOLOGY VIEW - Organizations -> Networks -> Devices
MATCH (o:Organization)-[:HAS_NETWORK]->(n:Network)-[:CONTAINS]->(d:Device)
RETURN o.name as Organization,
       n.name as Network,
       count(d) as DeviceCount,
       collect(DISTINCT d.device_type) as DeviceTypes,
       collect(DISTINCT d.status) as StatusSummary;

// 4. DEVICE HEALTH STATUS with Performance Metrics
MATCH (d:Device)
OPTIONAL MATCH (d)-[:HAS_METRIC]->(m:PerformanceMetric)
RETURN d.name as Device,
       d.platform as Platform,
       d.health_score as HealthScore,
       d.uptime_percentage as Uptime,
       d.status as Status,
       d.last_seen as LastSeen,
       collect(m.metric_type + ': ' + toString(m.value)) as Metrics;

// 5. SECURITY POSTURE - Threats and Vulnerabilities
MATCH (d:Device)
OPTIONAL MATCH (d)<-[:THREATENS]-(t:ThreatEvent)
OPTIONAL MATCH (d)-[:HAS_VULNERABILITY]->(v:Vulnerability)
RETURN d.name as Device,
       d.platform as Platform,
       d.location as Location,
       count(t) as ActiveThreats,
       count(v) as Vulnerabilities,
       collect(DISTINCT t.severity) as ThreatLevels,
       collect(DISTINCT v.severity) as VulnerabilitySeverity;

// 6. CONFIGURATION STATE - Current vs Desired
MATCH (d:Device)
OPTIONAL MATCH (d)-[:HAS_CONFIG]->(c:Configuration)
RETURN d.name as Device,
       d.platform as Platform,
       c.config_version as CurrentVersion,
       c.desired_version as DesiredVersion,
       c.compliance_status as ComplianceStatus,
       c.last_updated as LastConfigUpdate;

// 7. CHANGE HISTORY - Configuration Changes and Impact
MATCH (d:Device)-[:HAS_CHANGE_RECORD]->(ch:ChangeRecord)
RETURN d.name as Device,
       ch.change_type as ChangeType,
       ch.timestamp as ChangeTime,
       ch.change_description as Description,
       ch.impact_assessment as Impact,
       ch.success_status as Status
ORDER BY ch.timestamp DESC
LIMIT 50;

// 8. NETWORK TOPOLOGY VISUALIZATION - Graph View
MATCH (o:Organization)-[:HAS_NETWORK]->(n:Network)-[:CONTAINS]->(d:Device)
OPTIONAL MATCH (d)-[r:CONNECTED_TO]->(d2:Device)
RETURN o, n, d, d2, r;

// 9. CRITICAL DEVICES REQUIRING ATTENTION
MATCH (d:Device)
WHERE d.health_score < 80 OR d.status <> 'online'
OPTIONAL MATCH (d)<-[:THREATENS]-(t:ThreatEvent)
RETURN d.name as Device,
       d.platform as Platform,
       d.health_score as HealthScore,
       d.status as Status,
       d.location as Location,
       count(t) as SecurityThreats,
       d.issues as KnownIssues
ORDER BY d.health_score ASC;

// 10. PERFORMANCE TRENDS - Historical Baseline Analysis
MATCH (d:Device)-[:HAS_METRIC]->(m:PerformanceMetric)
WHERE m.timestamp > datetime() - duration('P30D')
RETURN d.name as Device,
       m.metric_type as MetricType,
       avg(m.value) as Average,
       min(m.value) as Minimum,
       max(m.value) as Maximum,
       count(m) as DataPoints
ORDER BY d.name, m.metric_type;

// 11. PLATFORM DISTRIBUTION SUMMARY
MATCH (d:Device)
RETURN d.platform as Platform,
       count(d) as DeviceCount,
       collect(DISTINCT d.device_type) as DeviceTypes,
       avg(d.health_score) as AvgHealthScore,
       sum(CASE WHEN d.status = 'online' THEN 1 ELSE 0 END) as OnlineDevices;

// 12. LOCATION-BASED TOPOLOGY
MATCH (d:Device)
WITH d, split(d.location, ' / ') as locationParts
RETURN locationParts[0] as Organization,
       locationParts[1] as Site,
       count(d) as DeviceCount,
       collect(DISTINCT d.device_type) as DeviceTypes,
       avg(d.health_score) as AvgHealth
ORDER BY Organization, Site;