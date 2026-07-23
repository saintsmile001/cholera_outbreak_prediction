"""
Email service for dispatching structured prediction reports via SMTP.

Uses Gmail SMTP with App Password authentication.
Sender: choleraguard@gmail.com
"""

import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


def build_email_html(
    recipient: str,
    dataset_name: str,
    summary_by_lga: list[dict[str, Any]],
) -> str:
    """Build a structured HTML email body with grouped LGA risk predictions."""

    # Build the grouped LGA table rows
    table_rows = ""
    for item in summary_by_lga:
        risk = (item.get("highest_risk_level") or "unknown").upper()
        avg_prob = round((item.get("average_probability") or 0) * 100, 1)
        max_prob = round((item.get("max_probability") or 0) * 100, 1)
        total = item.get("total_records") or 0
        location = item.get("location") or "Unknown LGA"

        risk_color = "#ef4444" if risk == "HIGH" else "#f59e0b" if risk == "MODERATE" else "#22c55e"

        table_rows += f"""
        <tr>
          <td style="padding:10px 14px; font-weight:600; color:#0f172a;">{location}</td>
          <td style="padding:10px 14px; text-align:center; color:#475569;">{total}</td>
          <td style="padding:10px 14px; text-align:center; font-weight:700; color:#0891b2;">{avg_prob}%</td>
          <td style="padding:10px 14px; text-align:center; font-weight:700; color:#0891b2;">{max_prob}%</td>
          <td style="padding:10px 14px; text-align:center;">
            <span style="background:{risk_color}22; color:{risk_color}; border:1px solid {risk_color}55;
                   padding:3px 10px; border-radius:9999px; font-size:11px; font-weight:700;">{risk}</span>
          </td>
        </tr>
        """

    lga_count = len(summary_by_lga)
    total_records = sum(item.get("total_records") or 0 for item in summary_by_lga)
    high_risk_lgas = [
        item.get("location", "") for item in summary_by_lga
        if (item.get("highest_risk_level") or "").lower() == "high"
    ]
    high_risk_text = ", ".join(high_risk_lgas) if high_risk_lgas else "None detected"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CholeraGuard Prediction Report</title>
</head>
<body style="margin:0; padding:0; background:#f1f5f9; font-family: 'Segoe UI', Arial, sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9; padding:32px 0;">
    <tr>
      <td align="center">
        <table width="640" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:16px;
               overflow:hidden; box-shadow:0 4px 24px rgba(0,0,0,0.08);">

          <!-- Header Banner -->
          <tr>
            <td style="background:linear-gradient(135deg,#0f172a 0%,#0e3a5e 100%); padding:32px 36px;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td>
                    <div style="font-size:11px; letter-spacing:2px; text-transform:uppercase;
                                color:#38bdf8; margin-bottom:8px;">CholeraGuard AI System</div>
                    <h1 style="margin:0; font-size:22px; font-weight:700; color:#ffffff;">
                      Cholera Outbreak Risk<br>Prediction Report
                    </h1>
                    <div style="margin-top:10px; font-size:13px; color:#94a3b8;">
                      Dataset: <strong style="color:#e2e8f0;">{dataset_name}</strong>
                    </div>
                  </td>
                  <td align="right" valign="top">
                    <div style="background:#ef444422; border:1px solid #ef444455; border-radius:10px;
                                padding:12px 18px; text-align:center;">
                      <div style="font-size:28px; font-weight:800; color:#ef4444;">{lga_count}</div>
                      <div style="font-size:11px; color:#94a3b8; margin-top:2px;">LGAs Evaluated</div>
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Summary Stats -->
          <tr>
            <td style="padding:24px 36px 0 36px;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td width="33%" style="text-align:center; padding:16px; background:#f8fafc;
                                         border-radius:12px; margin-right:8px;">
                    <div style="font-size:22px; font-weight:800; color:#0f172a;">{lga_count}</div>
                    <div style="font-size:11px; color:#64748b; margin-top:4px;">Local Governments</div>
                  </td>
                  <td width="4%"></td>
                  <td width="33%" style="text-align:center; padding:16px; background:#f8fafc; border-radius:12px;">
                    <div style="font-size:22px; font-weight:800; color:#0f172a;">{total_records}</div>
                    <div style="font-size:11px; color:#64748b; margin-top:4px;">Records Processed</div>
                  </td>
                  <td width="4%"></td>
                  <td width="33%" style="text-align:center; padding:16px; background:#fef2f2; border-radius:12px;">
                    <div style="font-size:22px; font-weight:800; color:#ef4444;">{len(high_risk_lgas)}</div>
                    <div style="font-size:11px; color:#64748b; margin-top:4px;">High Risk LGAs</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:24px 36px;">
              <p style="color:#334155; font-size:14px; line-height:1.7; margin:0 0 16px 0;">
                Dear Health Officer,
              </p>
              <p style="color:#334155; font-size:14px; line-height:1.7; margin:0 0 24px 0;">
                The CholeraGuard AI system has completed its epidemiological risk evaluation for
                <strong>{dataset_name}</strong>. Below is a full breakdown of outbreak probability
                scores across all {lga_count} Local Government Areas in the dataset.
              </p>

              <!-- LGA Table -->
              <h2 style="font-size:14px; font-weight:700; color:#0f172a; margin:0 0 12px 0;
                         text-transform:uppercase; letter-spacing:0.5px;">
                Grouped LGA Outbreak Risk Summary
              </h2>
              <div style="overflow:hidden; border-radius:12px; border:1px solid #e2e8f0;">
                <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
                  <thead>
                    <tr style="background:#0f172a;">
                      <th style="padding:12px 14px; text-align:left; font-size:11px; font-weight:600;
                                 color:#94a3b8; text-transform:uppercase; letter-spacing:0.5px;">LGA Location</th>
                      <th style="padding:12px 14px; text-align:center; font-size:11px; font-weight:600;
                                 color:#94a3b8; text-transform:uppercase; letter-spacing:0.5px;">Records</th>
                      <th style="padding:12px 14px; text-align:center; font-size:11px; font-weight:600;
                                 color:#94a3b8; text-transform:uppercase; letter-spacing:0.5px;">Avg Probability</th>
                      <th style="padding:12px 14px; text-align:center; font-size:11px; font-weight:600;
                                 color:#94a3b8; text-transform:uppercase; letter-spacing:0.5px;">Peak Probability</th>
                      <th style="padding:12px 14px; text-align:center; font-size:11px; font-weight:600;
                                 color:#94a3b8; text-transform:uppercase; letter-spacing:0.5px;">Risk Level</th>
                    </tr>
                  </thead>
                  <tbody style="background:#ffffff;">
                    {table_rows}
                  </tbody>
                </table>
              </div>

              <!-- High Risk Alert -->
              {"" if not high_risk_lgas else f'''
              <div style="margin-top:20px; padding:16px 20px; background:#fef2f2; border-left:4px solid #ef4444;
                           border-radius:8px;">
                <p style="margin:0; font-size:13px; font-weight:700; color:#dc2626;">
                  ⚠ High Risk LGAs Requiring Immediate Intervention:
                </p>
                <p style="margin:6px 0 0 0; font-size:13px; color:#7f1d1d;">{high_risk_text}</p>
              </div>
              '''}

              <!-- Recommendations -->
              <div style="margin-top:20px; padding:16px 20px; background:#f0f9ff; border-left:4px solid #0891b2;
                           border-radius:8px;">
                <p style="margin:0 0 8px 0; font-size:13px; font-weight:700; color:#0e7490;">
                  Recommended Action Guidelines
                </p>
                <ul style="margin:0; padding-left:18px; color:#334155; font-size:13px; line-height:1.8;">
                  <li>Deploy clean water chlorination tablets to High Risk LGAs immediately.</li>
                  <li>Pre-position Oral Rehydration Salts (ORS) and IV fluids at primary healthcare centers.</li>
                  <li>Maintain active daily surveillance across IDP settlement camps.</li>
                  <li>Alert community health workers in affected LGAs for door-to-door monitoring.</li>
                </ul>
              </div>

              <p style="margin:24px 0 0 0; font-size:13px; color:#64748b; line-height:1.7;">
                This report was generated automatically by the <strong>CholeraGuard AI Surveillance System</strong>.
                Do not reply to this email. For support, contact your system administrator.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f8fafc; padding:20px 36px; border-top:1px solid #e2e8f0;
                        text-align:center;">
              <p style="margin:0; font-size:11px; color:#94a3b8;">
                CholeraGuard AI &bull; Borno State Cholera Surveillance &bull;
                <a href="mailto:choleraguard@gmail.com" style="color:#0891b2;">choleraguard@gmail.com</a>
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def send_prediction_email(
    recipient_email: str,
    dataset_name: str,
    summary_by_lga: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Send a structured cholera prediction report email via Gmail SMTP (SSL port 465).

    Args:
        recipient_email: Destination email address (logged-in user).
        dataset_name: Name of the uploaded dataset file.
        summary_by_lga: List of per-LGA prediction summary dicts.

    Returns:
        dict with success status and message.

    Raises:
        RuntimeError: If SMTP connection or authentication fails.
    """
    sender_email = settings.SMTP_USER
    sender_name = settings.SENDER_NAME
    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    smtp_password = settings.SMTP_PASSWORD

    logger.info("[EMAIL] === Prediction Email Dispatch Started ===")
    logger.info("[EMAIL] Recipient     : %s", recipient_email)
    logger.info("[EMAIL] Dataset       : %s", dataset_name)
    logger.info("[EMAIL] LGAs in report: %d", len(summary_by_lga))
    logger.info("[EMAIL] SMTP Host     : %s", smtp_host)
    logger.info("[EMAIL] SMTP Port     : %s", smtp_port)
    logger.info("[EMAIL] SMTP User     : %s", sender_email)
    logger.info("[EMAIL] Password set  : %s", "YES" if smtp_password else "NO — SMTP_PASSWORD missing!")

    if not smtp_password:
        logger.error("[EMAIL] ABORT — SMTP_PASSWORD is empty. Check Railway environment variables.")
        return {
            "success": False,
            "message": "SMTP_PASSWORD not configured. Check Railway environment variables.",
        }

    logger.info("[EMAIL] Building HTML email body...")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Cholera Outbreak Risk Prediction Report — {dataset_name}"
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = recipient_email

    html_body = build_email_html(recipient_email, dataset_name, summary_by_lga)
    msg.attach(MIMEText(html_body, "html"))
    logger.info("[EMAIL] Email body built successfully (%d chars)", len(html_body))

    try:
        logger.info("[EMAIL] Connecting to SMTP server %s:%s...", smtp_host, smtp_port)
        context = ssl.create_default_context()

        if int(smtp_port) == 587:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
                logger.info("[EMAIL] SMTP connection established. Starting TLS...")
                server.starttls(context=context)
                logger.info("[EMAIL] Authenticating...")
                server.login(sender_email, smtp_password)
                logger.info("[EMAIL] Authentication successful. Sending email...")
                server.sendmail(sender_email, [recipient_email], msg.as_string())
                logger.info("[EMAIL] Email sent successfully to %s", recipient_email)
        else:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=30) as server:
                logger.info("[EMAIL] SMTP connection established. Authenticating...")
                server.login(sender_email, smtp_password)
                logger.info("[EMAIL] Authentication successful. Sending email...")
                server.sendmail(sender_email, [recipient_email], msg.as_string())
                logger.info("[EMAIL] Email sent successfully to %s", recipient_email)
    except smtplib.SMTPAuthenticationError as auth_err:
        logger.error("[EMAIL] SMTP Authentication FAILED: %s", str(auth_err))
        logger.error("[EMAIL] Hint: Ensure SMTP_PASSWORD is the Gmail App Password (not your Gmail login password).")
        raise
    except smtplib.SMTPConnectError as conn_err:
        logger.error("[EMAIL] SMTP Connection FAILED to %s:%s — %s", smtp_host, smtp_port, str(conn_err))
        raise
    except smtplib.SMTPException as smtp_err:
        logger.error("[EMAIL] SMTP Error: %s", str(smtp_err))
        raise
    except OSError as os_err:
        logger.error("[EMAIL] Network/OS Error during SMTP: %s", str(os_err))
        logger.error("[EMAIL] Hint: Railway may block outbound port 465. Try port 587 with STARTTLS.")
        raise

    logger.info("[EMAIL] === Email Dispatch Complete ===")
    return {
        "success": True,
        "message": f"Prediction report dispatched to {recipient_email} from {sender_email}",
    }
