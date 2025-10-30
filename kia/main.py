# kia/main.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import jinja2
import os

# Load data
df = pd.read_csv("data/jira_filter.csv")
df['Created'] = pd.to_datetime(df['Created'])
df['Resolved'] = pd.to_datetime(df['Resolved'])

# Compute resolution time
df['Resolution Time (days)'] = (df['Resolved'] - df['Created']).dt.days
resolved_tickets = df[df['Resolved'].notna()]

# Metrics
total_tickets = len(df)
resolved_count = len(resolved_tickets)
avg_resolution_time = resolved_tickets['Resolution Time (days)'].mean()
closed_within_3_days = (resolved_tickets['Resolution Time (days)'] <= 3).mean() * 100
top_assignee = resolved_tickets['Assignee'].value_counts().idxmax()
open_tickets = df[df['Resolved'].isna() & (df['Status'] != 'Monitoring')]

# Bar chart: ticket count by assignee
plt.figure(figsize=(6, 4))
ax = sns.countplot(data=df, x='Assignee', order=df['Assignee'].value_counts().index)
ax.set_title("Ticket Volume by Assignee")
plt.tight_layout()
os.makedirs("reports", exist_ok=True)
plt.savefig("reports/tickets_by_assignee.png")
plt.close()

# HTML Report
env = jinja2.Environment()
template_str = """
<!DOCTYPE html>
<html>
<head>
    <title>KiA Field Escalation Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #2c3e50; }
        table { border-collapse: collapse; width: 60%; margin-bottom: 40px; }
        th, td { text-align: left; padding: 8px; border: 1px solid #ddd; }
        th { background-color: #f4f4f4; }
        img { max-width: 500px; }
    </style>
</head>
<body>
    <h1>Know it All (KiA) - Field Escalation QC Report</h1>
    <h2>Summary</h2>
    <table>
        <tr><th>Total Tickets</th><td>{{ total_tickets }}</td></tr>
        <tr><th>Resolved Tickets</th><td>{{ resolved_count }}</td></tr>
        <tr><th>Avg Resolution Time (days)</th><td>{{ avg_resolution_time }}</td></tr>
        <tr><th>% Closed in ≤ 3 Days</th><td>{{ closed_within_3_days }}%</td></tr>
        <tr><th>Top Assignee</th><td>{{ top_assignee }}</td></tr>
    </table>

    <h2>Ticket Volume by Assignee</h2>
    <img src="tickets_by_assignee.png" alt="Tickets by Assignee">

    <h2>Open Tickets (Unresolved)</h2>
    <table>
        <tr><th>Ticket ID</th><th>Created</th><th>Assignee</th><th>Customer</th><th>Status</th></tr>
        {% for row in open_tickets %}
        <tr>
            <td>{{ row['Ticket ID'] }}</td>
            <td>{{ row['Created'].strftime('%Y-%m-%d') }}</td>
            <td>{{ row['Assignee'] }}</td>
            <td>{{ row['Customer'] }}</td>
            <td>{{ row['Status'] }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

template = env.from_string(template_str)
html_out = template.render(
    total_tickets=total_tickets,
    resolved_count=resolved_count,
    avg_resolution_time=round(avg_resolution_time, 2),
    closed_within_3_days=round(closed_within_3_days, 1),
    top_assignee=top_assignee,
    open_tickets=open_tickets.to_dict(orient='records')
)

# Save report
with open("reports/kia_field_qc_report.html", "w") as f:
    f.write(html_out)

print("✅ KiA Report generated: reports/kia_field_qc_report.html")
