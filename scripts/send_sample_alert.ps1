# Sends a sample Alertmanager-style payload to the AIOps API
$payload = @{
  version = "4"
  groupKey = "example-group"
  status = "firing"
  receiver = "aiops-webhook"
  groupLabels = @{ alertname = "HighCPU" }
  commonLabels = @{ severity = "warning"; service = "demo-service"; instance = "vm-001:9100" }
  commonAnnotations = @{ summary = "CPU usage high" }
  externalURL = "http://alertmanager.local"
  alerts = @(
    @{
      status = "firing"
      labels = @{
        alertname = "HighCPU"
        severity = "warning"
        service = "demo-service"
        instance = "vm-001:9100"
        job = "demo-service"
      }
      annotations = @{ summary = "CPU load above threshold" }
      startsAt = "2025-01-01T00:00:00Z"
      endsAt = ""
      generatorURL = "http://prometheus.local"
    }
  )
}

Invoke-WebRequest -Uri "http://localhost:8000/alert" -Method POST -Body ($payload | ConvertTo-Json -Depth 6) -ContentType "application/json" | Select-Object -ExpandProperty Content
