import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from datetime import date, timedelta
import json

def render_custom_table(df):
    """
    Renders a custom HTML table with the booking data
    
    Args:
        df: pandas DataFrame with booking data
    """
    
    # Convert DataFrame to JSON
    df_json = df.to_json(orient='records')
    
    # Read the HTML template
    with open('frontend/custom_table.html', 'r') as f:
        html_template = f.read()
    
    # Inject the data into the HTML
    html_with_data = html_template.replace(
        "window.parent.postMessage({ type: 'REQUEST_DATA' }, '*');",
        f"""
        // Auto-populate with data
        const bookingsData = {df_json};
        populateTable(bookingsData);
        """
    )
    
    # Render the component
    result = components.html(
        html_with_data,
        height=600,
        scrolling=True
    )
    
    return result


def render_interactive_table(df):
    """
    Renders a custom HTML table with the booking data (display only)
    
    Args:
        df: pandas DataFrame with booking data
    """
    
    # Convert DataFrame to JSON
    df_json = df.to_json(orient='records')
    
    # Create the HTML component for display
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: transparent;
            }}

            .table-container {{
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
            }}

            thead {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}

            thead th {{
                padding: 16px 12px;
                text-align: left;
                font-weight: 600;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            tbody tr {{
                border-bottom: 1px solid #e9ecef;
                transition: all 0.2s ease;
            }}

            tbody tr:hover {{
                background-color: #f8f9fa;
                transform: translateX(2px);
            }}

            tbody tr.checkout-soon {{
                background-color: #ffebee;
            }}

            tbody tr.checkout-soon:hover {{
                background-color: #ffcdd2;
            }}

            tbody tr.checkin-soon {{
                background-color: #e8f5e8;
            }}

            tbody tr.checkin-soon:hover {{
                background-color: #c8e6c9;
            }}

            tbody td {{
                padding: 14px 12px;
                font-size: 14px;
                color: #212529;
            }}

            .badge {{
                display: inline-block;
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                background-color: #e7f5ff;
                color: #1971c2;
            }}

            .booking-id {{
                font-weight: 600;
                color: #495057;
            }}

            .btn-placeholder {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
                cursor: not-allowed;
                opacity: 0.7;
            }}
        </style>
    </head>
    <body>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Booking ID</th>
                        <th>Guest Name</th>
                        <th>Check-In</th>
                        <th>Check-Out</th>
                        <th>Nights</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody id="tableBody"></tbody>
            </table>
        </div>

        <script>
            const bookingsData = {df_json};

            function parseDate(dateStr) {{
                return new Date(dateStr);
            }}

            function daysUntil(dateStr) {{
                const target = parseDate(dateStr);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                const diffTime = target - today;
                return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            }}

            function getRowClass(checkIn, checkOut) {{
                const daysToCheckout = daysUntil(checkOut);
                const daysToCheckin = daysUntil(checkIn);

                if (daysToCheckout <= 2) {{
                    return 'checkout-soon';
                }} else if (daysToCheckin <= 2 && daysToCheckin >= 0) {{
                    return 'checkin-soon';
                }}
                return '';
            }}

            const tbody = document.getElementById('tableBody');
            
            bookingsData.forEach((booking, index) => {{
                const row = document.createElement('tr');
                const rowClass = getRowClass(booking['Check-In'], booking['Check-Out']);
                if (rowClass) {{
                    row.className = rowClass;
                }}

                row.innerHTML = `
                    <td><span class="booking-id">${{booking['Booking ID']}}</span></td>
                    <td>${{booking['Name and Surname']}}</td>
                    <td>${{booking['Check-In']}}</td>
                    <td>${{booking['Check-Out']}}</td>
                    <td><span class="badge">${{booking['Nº Nights']}} nights</span></td>
                    <td>
                        <button class="btn-placeholder" title="Use button below table">
                            📋 Row ${{index + 1}}
                        </button>
                    </td>
                `;

                tbody.appendChild(row);
            }});
        </script>
    </body>
    </html>
    """
    
    # Render the component for display
    components.html(html_code, height=400, scrolling=True)
