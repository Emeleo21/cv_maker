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
st.set_page_config(page_title="CV Maker by LeoPython", page_icon="📄")
st.title("📄 CV Maker by LeoPython")
st.caption("Fill in your details, then download an ATS-friendly PDF.")


st.info(
    "📱 **Works on phone and PC.** Just fill in the boxes. Everything you type "
    "is saved when you tap **Generate CV** at the bottom, so there is no need "
    "to press Enter or Ctrl + Enter."
)


with st.expander("📖 How to use this CV Maker", expanded=False):
    st.markdown(
        """
1. **Step 1:** choose how many jobs and education entries you want, and pick a template.
2. **Step 2:** fill in the boxes from top to bottom. You can type freely.
3. **Skills:** separate them with commas, e.g. `Excel, Communication`.
4. **Achievements:** write one per line, starting with an action word and
   including numbers where you can (e.g. *Handled 50+ customer calls daily*).
5. Tap **Generate CV** at the bottom, then **Download PDF**.
6. Open the PDF and check that every detail appears. If you want to change
   something, edit the box and tap **Generate CV** again.
"""
    )


# ----- Step 1: setup (these save as soon as you tap a choice) -----
st.subheader("Step 1: Choose your setup")
n_jobs = st.selectbox("How many jobs do you want to list?", list(range(0, 9)), index=1)
n_edu = st.selectbox("How many education entries?", list(range(0, 6)), index=1)
template = st.radio("Template", TEMPLATES, horizontal=True)
accent = "#1F4E79"
if template.startswith("Modern"):
    accent = st.color_picker("Accent colour", "#1F4E79")


# ----- Step 2: the form (everything is saved when you tap Generate CV) -----
st.subheader("Step 2: Fill in your details")
with st.form("cv_form"):
    st.markdown("**Personal details**")
    name = st.text_input("Full name")
    c1, c2 = st.columns(2)
    email = c1.text_input("Email")
    phone = c2.text_input("Phone")
    location = c1.text_input("Location (e.g. Lagos, Nigeria)")
    linkedin = c2.text_input("LinkedIn / portfolio (optional)")


    st.markdown("**Professional summary**")
    summary = st.text_area("2-4 sentences about you", height=110)


    st.markdown("**Skills**")
    skills = st.text_input("Separate with commas",
                           placeholder="Customer service, Excel, Communication")


    jobs = []
    if n_jobs:
        st.markdown("**Work experience**")
    for i in range(int(n_jobs)):
        with st.expander(f"Job {i + 1}", expanded=(i == 0)):
            title = st.text_input("Job title", key=f"title{i}")
            company = st.text_input("Company", key=f"company{i}")
            d1, d2 = st.columns(2)
            dates = d1.text_input("Dates (e.g. Jan 2022 - Present)", key=f"dates{i}")
            jloc = d2.text_input("Location", key=f"jloc{i}")
            bullets = st.text_area("Achievements (one per line)",
                                   key=f"bullets{i}", height=120)
            jobs.append({"title": title, "company": company, "dates": dates,
                         "location": jloc, "bullets": bullets})


    edus = []
    if n_edu:
        st.markdown("**Education**")
    for i in range(int(n_edu)):
        with st.expander(f"Education {i + 1}", expanded=(i == 0)):
            degree = st.text_input("Degree / certificate", key=f"degree{i}")
            school = st.text_input("School", key=f"school{i}")
            edates = st.text_input("Dates", key=f"edates{i}")
            edus.append({"degree": degree, "school": school, "dates": edates})


    submitted = st.form_submit_button("Generate CV", type="primary")


if submitted:
    if not name.strip():
        st.error("Please enter your full name.")
        st.session_state.pop("cv_pdf", None)
    else:
        st.session_state["cv_pdf"] = build_pdf({
            "name": name.strip(), "email": email.strip(), "phone": phone.strip(),
            "location": location.strip(), "linkedin": linkedin.strip(),
            "summary": summary, "skills": skills, "jobs": jobs, "edus": edus,
        }, template=template, accent=accent)
        st.session_state["cv_filename"] = f"{name.strip().replace(' ', '_')}_CV.pdf"


# The download button sits outside the form (Streamlit does not allow it inside)
if "cv_pdf" in st.session_state:
    st.success("Your CV is ready!")
    st.download_button("⬇️ Download PDF", data=st.session_state["cv_pdf"],
                       file_name=st.session_state["cv_filename"],
                       mime="application/pdf")
    st.caption("Changed something? Edit the boxes and tap Generate CV again.")











