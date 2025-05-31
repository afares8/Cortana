import logging
import os
from datetime import datetime
from pathlib import Path
import jinja2
from weasyprint import HTML

logger = logging.getLogger(__name__)

class PDFGenerator:
    """
    Utility class for generating PDF reports using WeasyPrint.
    """
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.reports_dir = Path.home() / "repos" / "Cortana" / "backend" / "data" / "uaf_reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_dir),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
        )
    
    def generate_pdf(self, template_name, context, output_path):
        """
        Generate a PDF file using a Jinja2 template and context data.
        
        Args:
            template_name: Name of the Jinja2 template file
            context: Dictionary with data to render in the template
            output_path: Path where the PDF file will be saved
            
        Returns:
            Path to the generated PDF file
        """
        try:
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(**context)
            
            html = HTML(string=html_content)
            html.write_pdf(output_path)
            
            logger.info(f"PDF generated successfully at {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise

pdf_generator = PDFGenerator()

async def generate_uaf_report_pdf(report, pdf_output_path=None):
    """
    Generate a UAF (Ultimate Beneficial Owner) report PDF.
    
    Args:
        report: ComplianceReport object containing report data
        pdf_output_path: Optional path where the PDF should be saved
        
    Returns:
        Path to the generated PDF file
    """
    try:
        report_data = report.report_data if hasattr(report, "report_data") else {}
        client_id = report.client_id if hasattr(report, "client_id") else "unknown"
        client_name = report.client_name if hasattr(report, "client_name") else "Unknown Client"
        
        if pdf_output_path:
            output_path = Path(pdf_output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"uaf_client_{client_id}_{timestamp}.pdf"
            output_dir = Path.home() / "repos" / "Cortana" / "backend" / "data" / "uaf_reports"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / filename
        
        context = {
            **report_data,
            "client": report_data.get("client"),
            "timestamp": report_data.get("timestamp"),
            "screening_result": report_data.get("screening_result"),
            "matches": report_data.get("matches"),
            "country_risk": report_data.get("country_risk"),
            "sources": report_data.get("sources"),
            "data_updated": report_data.get("data_updated"),
            "report_uuid": report_data.get("report_uuid"),
            "client_name": client_name,
            "client_id": client_id,
            "generated_at": datetime.now().isoformat(),
            "report_type": "UAF Report",
        }
        
        pdf_path = pdf_generator.generate_pdf("uaf_report.html", context, str(output_path))
        
        if hasattr(report, "report_path"):
            report.report_path = str(pdf_path)
        
        logger.info(f"UAF report generated for client {client_id} at {pdf_path}")
        return pdf_path
    except Exception as e:
        logger.error(f"Error generating UAF report: {str(e)}")
        raise
