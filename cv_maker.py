import io
from xml.sax.saxutils import escape


import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable




# ---------- PDF BUILDER (single column, standard font = ATS-friendly) ----------
TEMPLATES = ["Classic (black)", "Modern (coloured)"]




def build_pdf(data, template="Classic (black)", accent="#1F4E79"):
    modern = template.startswith("Modern")
    accent_color = colors.HexColor(accent) if modern else colors.black


    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm,
        title=f"{data['name']} - CV", author=data["name"],
    )


    # Classic: centred black name. Modern: left-aligned, larger, coloured name.
    name_style = ParagraphStyle(
        "Name", fontName="Helvetica-Bold",
        fontSize=24 if modern else 20, leading=28 if modern else 24,
        alignment=0 if modern else TA_CENTER,
        textColor=accent_color,
    )
    contact_style = ParagraphStyle(
        "Contact", fontName="Helvetica", fontSize=9.5, leading=13,
        alignment=0 if modern else TA_CENTER,
        textColor=colors.HexColor("#444444"),
    )
    heading_style = ParagraphStyle(
        "Heading", fontName="Helvetica-Bold", fontSize=11.5, leading=14,
        spaceBefore=12 if modern else 10, spaceAfter=2,
        textColor=accent_color,
    )
    body_style = ParagraphStyle("Body", fontName="Helvetica", fontSize=10, leading=14)
    role_style = ParagraphStyle("Role", fontName="Helvetica-Bold", fontSize=10.5,
                                leading=14, spaceBefore=5)
    date_style = ParagraphStyle("Date", fontName="Helvetica-Oblique", fontSize=9.5,
                                leading=12, textColor=colors.HexColor("#555555"))
    bullet_style = ParagraphStyle("Bullet", parent=body_style, leftIndent=12,
                                  bulletIndent=2)


    def P(text, style, **kw):
        return Paragraph(escape(text), style, **kw)


    def section(title):
        # Modern: thicker coloured line under each heading
        return [P(title.upper(), heading_style),
                HRFlowable(width="100%", thickness=1.8 if modern else 0.8,
                           color=accent_color, spaceAfter=4)]


    story = [P(data["name"], name_style)]
    contact = " | ".join(x for x in [data["email"], data["phone"],
                                      data["location"], data["linkedin"]] if x)
    if contact:
        story.append(P(contact, contact_style))


    if data["summary"].strip():
        story += section("Professional Summary")
        story.append(P(data["summary"].strip(), body_style))


    if data["skills"].strip():
        story += section("Skills")
        skills = [s.strip() for s in data["skills"].split(",") if s.strip()]
        story.append(P(", ".join(skills), body_style))


    jobs = [j for j in data["jobs"] if j["title"] or j["company"]]
    if jobs:
        story += section("Work Experience")
        for j in jobs:
            heading = j["title"] + (f" - {j['company']}" if j["company"] else "")
            story.append(P(heading, role_style))
            dates = " | ".join(x for x in [j["dates"], j["location"]] if x)
            if dates:
                story.append(P(dates, date_style))
            for line in j["bullets"].splitlines():
                line = line.strip().lstrip("-•* ").strip()
                if line:
                    story.append(P(line, bullet_style, bulletText="•"))


    edus = [e for e in data["edus"] if e["school"] or e["degree"]]
    if edus:
        story += section("Education")
        for e in edus:
            heading = e["degree"] + (f" - {e['school']}" if e["school"] else "")
            story.append(P(heading, role_style))
            if e["dates"]:
                story.append(P(e["dates"], date_style))


    doc.build(story)
    return buffer.getvalue()




# ---------- STREAMLIT APP ----------
st.set_page_config(page_title="CV Maker", page_icon="📄")
st.title("📄 CV Maker")
st.caption("Fill in your details, then download an ATS-friendly PDF.")


st.warning(
    "⚠️ **Important:** after typing in a box, press **Enter** (or click outside "
    "the box) so your details are saved. For the larger text boxes "
    "(summary and achievements), press **Ctrl + Enter**. Anything you don't "
    "confirm may be missing from your CV."
)


with st.expander("📖 How to use this CV Maker", expanded=False):
    st.markdown(
        """
1. **Fill in each section** from top to bottom.
2. **Press Enter after every entry** so it is saved. In the big boxes
   (summary and achievements) press **Ctrl + Enter** instead, because Enter
   only starts a new line there.
3. **Skills:** type them separated by commas, e.g. `Excel, Communication`, then press Enter.
4. **Achievements:** write one achievement per line, starting with an action
   word and including numbers where you can (e.g. *Handled 50+ customer calls daily*).
5. **Choose a template** (Classic or Modern). For Modern you can pick your own colour.
6. Click **Generate CV**, then **Download PDF**.
7. Open the PDF and check that every detail appears. If something is missing,
   go back, press Enter in that box, and generate again.
"""
    )


st.subheader("Personal details")
name = st.text_input("Full name")
c1, c2 = st.columns(2)
email = c1.text_input("Email")
phone = c2.text_input("Phone")
location = c1.text_input("Location (e.g. Lagos, Nigeria)")
linkedin = c2.text_input("LinkedIn / portfolio (optional)")


st.subheader("Professional summary")
summary = st.text_area("2-4 sentences about you (press Ctrl + Enter to save)", height=110)


st.subheader("Skills")
skills = st.text_input("Separate with commas",
                       placeholder="Customer service, Excel, Communication")


st.subheader("Work experience")
n_jobs = st.number_input("Number of jobs", min_value=0, max_value=8, value=1, step=1)
jobs = []
for i in range(int(n_jobs)):
    with st.expander(f"Job {i + 1}", expanded=(i == 0)):
        title = st.text_input("Job title", key=f"title{i}")
        company = st.text_input("Company", key=f"company{i}")
        d1, d2 = st.columns(2)
        dates = d1.text_input("Dates (e.g. Jan 2022 - Present)", key=f"dates{i}")
        jloc = d2.text_input("Location", key=f"jloc{i}")
        bullets = st.text_area("Achievements (one per line, press Ctrl + Enter to save)",
                               key=f"bullets{i}", height=120)
        jobs.append({"title": title, "company": company, "dates": dates,
                     "location": jloc, "bullets": bullets})


st.subheader("Education")
n_edu = st.number_input("Number of entries", min_value=0, max_value=5, value=1, step=1)
edus = []
for i in range(int(n_edu)):
    with st.expander(f"Education {i + 1}", expanded=(i == 0)):
        degree = st.text_input("Degree / certificate", key=f"degree{i}")
        school = st.text_input("School", key=f"school{i}")
        edates = st.text_input("Dates", key=f"edates{i}")
        edus.append({"degree": degree, "school": school, "dates": edates})


st.divider()
st.subheader("Template")
template = st.radio("Choose a style", TEMPLATES, horizontal=True)
accent = "#1F4E79"
if template.startswith("Modern"):
    accent = st.color_picker("Accent colour", "#1F4E79")


if st.button("Generate CV", type="primary"):
    if not name.strip():
        st.error("Please enter your full name.")
    else:
        pdf_bytes = build_pdf({
            "name": name.strip(), "email": email.strip(), "phone": phone.strip(),
            "location": location.strip(), "linkedin": linkedin.strip(),
            "summary": summary, "skills": skills, "jobs": jobs, "edus": edus,
        }, template=template, accent=accent)
        st.success("Your CV is ready!")
        st.download_button("⬇️ Download PDF", data=pdf_bytes,
                           file_name=f"{name.strip().replace(' ', '_')}_CV.pdf",
                           mime="application/pdf")









