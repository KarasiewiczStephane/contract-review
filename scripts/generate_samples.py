"""Generate sample contract PDFs for the dashboard."""

from pathlib import Path

from fpdf import FPDF

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample"

NDA_TEXT = """NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement ("Agreement") is entered into as of January 15, 2025, \
by and between TechCorp Inc., a Delaware corporation ("Disclosing Party"), and \
Acme Consulting LLC, a California limited liability company ("Receiving Party").

RECITALS

WHEREAS, the Disclosing Party possesses certain confidential and proprietary information \
relating to its business operations, technology, and trade secrets; and

WHEREAS, the Receiving Party desires to receive certain Confidential Information for the \
purpose of evaluating a potential business relationship between the parties;

NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree as follows:

1. DEFINITION OF CONFIDENTIAL INFORMATION

1.1 "Confidential Information" means any and all non-public information, in any form or \
medium, whether tangible or intangible, that is disclosed by the Disclosing Party to the \
Receiving Party, including but not limited to: (a) trade secrets, inventions, patents, \
copyrights, trademarks; (b) business plans, financial data, customer lists, marketing \
strategies; (c) software, algorithms, source code, technical specifications; and \
(d) any information marked as "confidential" or that a reasonable person would understand \
to be confidential.

1.2 Confidential Information shall not include information that: (a) is or becomes publicly \
available through no fault of the Receiving Party; (b) was known to the Receiving Party \
prior to disclosure; (c) is independently developed by the Receiving Party without use of \
Confidential Information; or (d) is disclosed with the prior written consent of the \
Disclosing Party.

2. OBLIGATIONS OF THE RECEIVING PARTY

2.1 The Receiving Party shall hold all Confidential Information in strict confidence and \
shall not disclose any Confidential Information to any third party without the prior written \
consent of the Disclosing Party.

2.2 The Receiving Party shall use the Confidential Information solely for the purpose of \
evaluating the potential business relationship and for no other purpose.

2.3 The Receiving Party shall protect the Confidential Information using the same degree of \
care it uses to protect its own confidential information, but in no event less than \
reasonable care.

3. TERM AND TERMINATION

3.1 This Agreement shall remain in effect for a period of three (3) years from the date \
first written above.

3.2 Upon termination or expiration of this Agreement, the Receiving Party shall promptly \
return or destroy all Confidential Information and any copies thereof.

3.3 The obligations of confidentiality shall survive termination of this Agreement for a \
period of five (5) years.

4. REMEDIES

4.1 The Receiving Party acknowledges that any breach of this Agreement may cause irreparable \
harm to the Disclosing Party and that monetary damages may be inadequate. Therefore, the \
Disclosing Party shall be entitled to seek equitable relief, including injunction and \
specific performance, in addition to all other remedies available at law or in equity.

5. INDEMNIFICATION

5.1 The Receiving Party shall indemnify, defend, and hold harmless the Disclosing Party \
from and against any and all claims, damages, losses, costs, and expenses (including \
reasonable attorneys' fees) arising out of or relating to any breach of this Agreement \
by the Receiving Party.

6. NON-SOLICITATION

6.1 During the term of this Agreement and for a period of two (2) years thereafter, the \
Receiving Party shall not, directly or indirectly, solicit or attempt to solicit any \
employee, contractor, or client of the Disclosing Party.

7. GOVERNING LAW AND JURISDICTION

7.1 This Agreement shall be governed by and construed in accordance with the laws of the \
State of Delaware, without regard to its conflict of laws principles.

7.2 Any dispute arising out of or relating to this Agreement shall be subject to the \
exclusive jurisdiction of the state and federal courts located in Wilmington, Delaware.

8. GENERAL PROVISIONS

8.1 This Agreement constitutes the entire agreement between the parties with respect to \
the subject matter hereof and supersedes all prior or contemporaneous agreements.

8.2 This Agreement may not be amended or modified except by a written instrument signed \
by both parties.

8.3 If any provision of this Agreement is held to be invalid or unenforceable, the remaining \
provisions shall continue in full force and effect.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

DISCLOSING PARTY: TechCorp Inc.
By: ___________________________
Name: John Smith
Title: Chief Executive Officer

RECEIVING PARTY: Acme Consulting LLC
By: ___________________________
Name: Jane Doe
Title: Managing Partner
"""

SERVICE_AGREEMENT_TEXT = """MASTER SERVICE AGREEMENT

This Master Service Agreement ("Agreement") is made and entered into as of March 1, 2025, \
by and between GlobalTech Solutions Inc., a New York corporation with offices at 500 Park \
Avenue, New York, NY 10022 ("Provider"), and DataFlow Analytics Corp., a Texas corporation \
with offices at 200 Commerce Street, Dallas, TX 75201 ("Client").

1. SERVICES

1.1 Scope. The Provider agrees to provide the Client with software development, data \
analytics, and cloud infrastructure management services as described in each Statement of \
Work ("SOW") executed under this Agreement.

1.2 Statements of Work. Each SOW shall specify: (a) the services to be performed; \
(b) deliverables; (c) timelines; (d) pricing; and (e) acceptance criteria.

1.3 Change Orders. Any changes to the scope of a SOW must be documented in a written \
Change Order signed by both parties.

2. COMPENSATION AND PAYMENT

2.1 Fees. The Client shall pay the Provider the fees set forth in each SOW. Unless otherwise \
specified, fees shall be billed monthly in arrears.

2.2 Payment Terms. All invoices are due and payable within thirty (30) days of the invoice \
date. Late payments shall accrue interest at the rate of 1.5% per month or the maximum rate \
permitted by law, whichever is less.

2.3 Expenses. The Client shall reimburse the Provider for all pre-approved, reasonable \
out-of-pocket expenses incurred in connection with the performance of services.

2.4 Taxes. All fees are exclusive of taxes. The Client shall be responsible for all \
applicable sales, use, and other taxes, excluding taxes based on the Provider's income.

3. TERM AND TERMINATION

3.1 Term. This Agreement shall commence on the date first written above and shall continue \
for an initial term of two (2) years, unless earlier terminated as provided herein.

3.2 Renewal. This Agreement shall automatically renew for successive one (1) year periods \
unless either party provides written notice of non-renewal at least ninety (90) days prior \
to the end of the then-current term.

3.3 Termination for Convenience. Either party may terminate this Agreement upon sixty (60) \
days prior written notice to the other party.

3.4 Termination for Cause. Either party may terminate this Agreement immediately upon \
written notice if the other party: (a) materially breaches this Agreement and fails to \
cure such breach within thirty (30) days of receiving notice; or (b) becomes insolvent, \
files for bankruptcy, or ceases to do business.

3.5 Effect of Termination. Upon termination, the Client shall pay all fees for services \
rendered through the date of termination.

4. INTELLECTUAL PROPERTY

4.1 Work Product. All work product, deliverables, and materials created by the Provider \
specifically for the Client under this Agreement ("Work Product") shall be the exclusive \
property of the Client upon full payment.

4.2 Pre-Existing IP. Each party retains all rights to its pre-existing intellectual \
property. The Provider grants the Client a non-exclusive, perpetual license to use any \
Provider pre-existing IP incorporated into the Work Product.

4.3 The Provider retains the right to use general knowledge, skills, and experience \
gained during the performance of services.

5. CONFIDENTIALITY

5.1 Each party agrees to maintain the confidentiality of the other party's Confidential \
Information and to use it only for purposes of this Agreement.

5.2 Confidential Information excludes information that is publicly available, independently \
developed, or rightfully received from a third party.

6. WARRANTIES AND DISCLAIMERS

6.1 The Provider warrants that: (a) services will be performed in a professional and \
workmanlike manner; (b) deliverables will conform to the specifications in the applicable \
SOW; and (c) the Provider has the right to enter into this Agreement.

6.2 EXCEPT AS EXPRESSLY SET FORTH HEREIN, THE PROVIDER MAKES NO OTHER WARRANTIES, \
EXPRESS OR IMPLIED, INCLUDING WARRANTIES OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR \
PURPOSE.

7. LIMITATION OF LIABILITY

7.1 IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, \
CONSEQUENTIAL, OR PUNITIVE DAMAGES, REGARDLESS OF THE CAUSE OF ACTION.

7.2 THE TOTAL AGGREGATE LIABILITY OF THE PROVIDER UNDER THIS AGREEMENT SHALL NOT EXCEED \
THE TOTAL FEES PAID BY THE CLIENT IN THE TWELVE (12) MONTHS PRECEDING THE CLAIM.

8. INDEMNIFICATION

8.1 The Provider shall indemnify the Client against any third-party claims arising from: \
(a) the Provider's negligence or willful misconduct; (b) infringement of third-party \
intellectual property rights by the Work Product; or (c) the Provider's breach of this Agreement.

8.2 The Client shall indemnify the Provider against any third-party claims arising from \
the Client's use of the Work Product in a manner not authorized by this Agreement.

9. DATA PROTECTION

9.1 The Provider shall comply with all applicable data protection laws, including GDPR \
and CCPA, in connection with any personal data processed under this Agreement.

9.2 The Provider shall implement appropriate technical and organizational measures to \
protect personal data against unauthorized access, loss, or destruction.

10. FORCE MAJEURE

10.1 Neither party shall be liable for any delay or failure to perform due to causes \
beyond its reasonable control, including natural disasters, war, terrorism, pandemics, \
or government actions.

11. GOVERNING LAW

11.1 This Agreement shall be governed by and construed in accordance with the laws of \
the State of New York.

11.2 Any disputes shall be resolved through binding arbitration administered by the \
American Arbitration Association in New York, NY.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

PROVIDER: GlobalTech Solutions Inc.
By: ___________________________
Name: Robert Williams
Title: VP of Business Development

CLIENT: DataFlow Analytics Corp.
By: ___________________________
Name: Sarah Johnson
Title: Chief Technology Officer
"""

EMPLOYMENT_CONTRACT_TEXT = """EMPLOYMENT AGREEMENT

This Employment Agreement ("Agreement") is entered into as of February 1, 2025, by and \
between InnovateTech Corp., a California corporation ("Employer"), and Michael Chen \
("Employee").

1. POSITION AND DUTIES

1.1 Position. The Employer hereby employs the Employee as Senior Software Engineer, \
reporting to the VP of Engineering.

1.2 Duties. The Employee shall perform such duties as are customarily associated with \
the position, including software development, code review, system architecture, and \
mentoring junior developers.

1.3 Full-Time Commitment. The Employee agrees to devote full-time professional efforts \
to the Employer and shall not engage in any other employment or consulting without prior \
written consent of the Employer.

2. COMPENSATION AND BENEFITS

2.1 Base Salary. The Employee shall receive an annual base salary of $185,000, payable \
in accordance with the Employer's standard payroll schedule, subject to applicable \
withholdings and deductions.

2.2 Signing Bonus. The Employee shall receive a one-time signing bonus of $25,000, payable \
within thirty (30) days of the start date. If the Employee voluntarily terminates employment \
within twelve (12) months, the signing bonus must be repaid in full.

2.3 Annual Bonus. The Employee shall be eligible for an annual performance bonus of up to \
20% of base salary, based on individual performance and company financial results, at the \
sole discretion of the Employer.

2.4 Equity. The Employee shall receive a stock option grant of 10,000 shares of the \
Employer's common stock, subject to a four (4) year vesting schedule with a one (1) year \
cliff, as detailed in the separate Stock Option Agreement.

2.5 Benefits. The Employee shall be eligible to participate in all benefit plans offered \
to similarly situated employees, including health insurance, dental insurance, vision \
insurance, 401(k) plan, and paid time off.

3. AT-WILL EMPLOYMENT

3.1 This employment is at-will. Either party may terminate the employment relationship \
at any time, with or without cause, and with or without notice.

3.2 Notwithstanding the at-will nature of employment, the Employer agrees to provide \
thirty (30) days written notice of termination without cause when practicable.

4. SEVERANCE

4.1 If the Employer terminates the Employee's employment without cause, the Employee \
shall be entitled to severance equal to three (3) months of base salary, subject to \
execution of a general release of claims.

4.2 If the Employee is terminated within twelve (12) months following a Change of Control, \
the Employee shall be entitled to severance equal to six (6) months of base salary plus \
accelerated vesting of 50% of unvested equity.

5. INTELLECTUAL PROPERTY

5.1 Assignment. The Employee agrees that all inventions, discoveries, improvements, works \
of authorship, and trade secrets conceived or developed during the course of employment \
and related to the Employer's business shall be the sole property of the Employer.

5.2 Prior Inventions. The Employee has listed on Exhibit A all prior inventions that the \
Employee wishes to exclude from this Agreement.

5.3 The Employee shall promptly disclose all inventions and assist the Employer in \
obtaining patents and other intellectual property protections.

6. CONFIDENTIALITY

6.1 The Employee shall not disclose any Confidential Information of the Employer during \
or after employment, except as required in the performance of duties.

6.2 Confidential Information includes trade secrets, customer data, financial information, \
product roadmaps, source code, algorithms, and business strategies.

7. NON-COMPETE AND NON-SOLICITATION

7.1 Non-Compete. For a period of one (1) year following termination, the Employee shall \
not engage in any business that directly competes with the Employer within a fifty (50) \
mile radius of any Employer office location.

7.2 Non-Solicitation of Employees. For a period of two (2) years following termination, \
the Employee shall not solicit or recruit any employee or contractor of the Employer.

7.3 Non-Solicitation of Customers. For a period of one (1) year following termination, \
the Employee shall not solicit business from any customer of the Employer with whom the \
Employee had contact during the last twelve (12) months of employment.

8. DISPUTE RESOLUTION

8.1 Any dispute arising under this Agreement shall first be submitted to mediation.

8.2 If mediation fails, disputes shall be resolved through binding arbitration in \
San Francisco, California, in accordance with the rules of JAMS.

9. GOVERNING LAW

9.1 This Agreement shall be governed by the laws of the State of California.

10. GENERAL PROVISIONS

10.1 This Agreement constitutes the entire agreement between the parties and supersedes \
all prior agreements.

10.2 This Agreement may be amended only by a written instrument signed by both parties.

10.3 If any provision is found unenforceable, the remaining provisions shall remain in \
full force and effect.

EMPLOYER: InnovateTech Corp.
By: ___________________________
Name: Lisa Park
Title: VP of Engineering

EMPLOYEE:
By: ___________________________
Name: Michael Chen
Date: February 1, 2025
"""

CONTRACTS = [
    ("sample_nda.pdf", "Non-Disclosure Agreement", NDA_TEXT),
    ("sample_service_agreement.pdf", "Master Service Agreement", SERVICE_AGREEMENT_TEXT),
    ("sample_employment_contract.pdf", "Employment Agreement", EMPLOYMENT_CONTRACT_TEXT),
]


def generate_pdf(filename: str, title: str, text: str) -> Path:
    """Generate a PDF contract from text."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)

    pdf.set_font("Helvetica", "", 10)
    for paragraph in text.strip().split("\n\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if paragraph.isupper() or (paragraph[0].isdigit() and paragraph.split(".")[0].isdigit() and len(paragraph) < 80 and "\n" not in paragraph):
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 5, paragraph)
            pdf.set_font("Helvetica", "", 10)
        else:
            pdf.multi_cell(0, 5, paragraph)
        pdf.ln(3)

    output = SAMPLE_DIR / filename
    pdf.output(str(output))
    return output


def main() -> None:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    for filename, title, text in CONTRACTS:
        path = generate_pdf(filename, title, text)
        print(f"Generated: {path}")


if __name__ == "__main__":
    main()
