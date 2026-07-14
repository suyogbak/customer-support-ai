import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Documents ka content aur unka data
documents_data = {
    "FAQ.pdf": """
    <b>TechMart Electronics - Frequently Asked Questions (FAQ)</b><br/><br/>
    Q1: What is the delivery time for products?<br/>
    A1: Standard shipping takes 3-5 business days. Express shipping takes 1-2 business days.<br/><br/>
    Q2: How can I track my order?<br/>
    A2: Once shipped, an email with a tracking number from our logistics partner will be sent to you.<br/><br/>
    Q3: Do you offer international shipping?<br/>
    A3: Currently, TechMart only ships within the country. International shipping is not available.
    """,
    
    "RefundPolicy.pdf": """
    <b>TechMart Electronics - Refund and Return Policy</b><br/><br/>
    1. Customers can request a full refund within 14 days of purchase if the product is unused and in original packaging.<br/><br/>
    2. If a customer pays for a Premium Subscription and features remain locked, the backend activation takes up to 2 hours. If it exceeds 24 hours, a full refund is initiated automatically.<br/><br/>
    3. Refund amount will be credited back to the original payment method within 5-7 working days.
    """,
    
    "ShippingPolicy.pdf": """
    <b>TechMart Electronics - Shipping & Delivery Policy</b><br/><br/>
    1. Shipping Charges: Free standard shipping on all orders above 4,999 INR. A flat fee of 150 INR applies to orders below that.<br/><br/>
    2. Damaged Shipments: If you receive a damaged package, please report it to our Complaint Agent within 24 hours with unboxing video proof.
    """,
    
    "Warranty.pdf": """
    <b>TechMart Electronics - Product Warranty Terms</b><br/><br/>
    1. All TechMart Pro Laptops and smartphones come with a standard 1-Year Limited Hardware Warranty.<br/><br/>
    2. The warranty covers manufacturing defects, screen flickering, and battery issues. It does NOT cover physical drops, liquid damage, or unauthorized repairs.<br/><br/>
    3. To claim warranty, customer must present the original invoice to the Technical Support Agent.
    """,
    
    "UserManual.pdf": """
    <b>TechMart Pro Laptop - User Manual & Troubleshooting</b><br/><br/>
    Product Specs: TechMart Pro Laptop features 16GB RAM, 512GB SSD, Intel i7 Processor, costing 50,000 INR.<br/><br/>
    Troubleshooting Guide:<br/>
    1. System Hangs/Errors: If you encounter installation errors or BSOD, completely uninstall the third-party application and update to TechMart OS Version 2.0.<br/><br/>
    2. Password Reset: Click the 'Forgot Password' link on the main login dashboard to receive an OTP on your registered email.
    """
}

def generate_pdfs():
    # Make sure folder exists
    output_dir = "../knowledge_base"
    os.makedirs(output_dir, exist_ok=True)
    
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    
    for filename, content in documents_data.items():
        filepath = os.path.join(output_dir, filename)
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        
        # Clean up text spaces
        paragraphs = [p.strip() for p in content.strip().split("<br/><br/>")]
        for para in paragraphs:
            story.append(Paragraph(para, normal_style))
            story.append(Spacer(1, 12))
            
        doc.build(story)
        print(f"✅ Generated: {filepath}")

if __name__ == "__main__":
    generate_pdfs()