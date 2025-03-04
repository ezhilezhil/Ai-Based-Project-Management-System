from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# AI API Configuration
API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = "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"  


@app.route("/", methods=["GET", "POST"])
def index():
    project_plan = None

    if request.method == "POST":
        # Get form data
        problem_statement = request.form["problem_statement"]
        team_size = int(request.form["team_size"])
        deadline = request.form["deadline"]

        # Collect team members and skills
        team_members = {}
        for i in range(1, team_size + 1):
            name = request.form[f"name_{i}"]
            skills = request.form[f"skills_{i}"].split(", ")
            team_members[name] = skills

        # Format data for AI
        formatted_skills = "\n".join([f"{name}: {', '.join(skills)}" for name, skills in team_members.items()])

        # AI prompt
        prompt = f"""
        Analyze the project details and generate the following **in order**:

        1. **Problem Statement** (Rephrase concisely).
        2. **Technologies** required for the project.
        3. **Specific Skills** required for implementation.
        4. **Identify Missing Skills** (Compare required vs. team skills).
        5. **Best Approach to Solve Skill Gaps**:
           - 📌 Train (if skills are learnable within the timeline)
           - 📌 Hire (if critical expertise is missing)
           - 📌 Use Alternative Tech (if possible)
        6. **Assign Skills to Team Members** (Based on available skills and the best approach).
        7. **Adjust Timeline** (If training is required, extend duration accordingly).
        8. **Milestones** with estimated completion weeks.

        📌 **Project Details:**
        - **Problem Statement:** {problem_statement}
        - **Team Members & Skills:** 
          {formatted_skills}
        - **Deadline:** {deadline}
        """

        # Call AI API
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are an AI project consultant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.9
        }

        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            project_plan = data["choices"][0]["message"]["content"]
        else:
            project_plan = f"❌ Error: {response.status_code}, {response.text}"

    return render_template("index.html", project_plan=project_plan)

if __name__ == "__main__":
    app.run(debug=True)
