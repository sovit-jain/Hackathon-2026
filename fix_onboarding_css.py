#!/usr/bin/env python3
import re

file_path = r"c:\Users\sovit\Hackathon-2026\skillbridge-mvp\frontend\src\app\onboarding\page.tsx"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace assessment step heading and paragraph styling
content = content.replace(
    '<h1 className="text-3xl font-semibold">Your first assessment</h1>',
    '<h1 className="text-3xl font-semibold text-slate-900">Your first assessment</h1>'
)

# Replace career goal select styling
content = content.replace(
    '<select value={goal} onChange={(e) => setGoal(e.target.value)} className="w-full rounded-xl border border-slate-300 px-3 py-2">',
    '<select value={goal} onChange={(e) => setGoal(e.target.value)} className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm">'
)

# Replace question container styling
content = content.replace(
    '<div key={question.id} className="rounded-2xl border border-slate-200 p-4">',
    '<div key={question.id} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">'
)

# Replace question text styling
content = content.replace(
    '<p className="font-medium">{question.text}</p>',
    '<p className="font-medium text-slate-900">{question.text}</p>'
)

# Replace option label styling - only the assessment section ones
old_label = '<label key={option} className={`flex items-center gap-3 rounded-xl border px-3 py-2 ${selected ? \'border-indigo-500 bg-indigo-50\' : \'border-slate-200\'}`}>'
new_label = '<label key={option} className={`flex items-center gap-3 rounded-xl border px-3 py-2 cursor-pointer ${selected ? \'border-indigo-500 bg-indigo-50\' : \'border-slate-200 bg-white\'}`}>'
content = content.replace(old_label, new_label)

# Replace option span styling
content = content.replace(
    '<span>{option}</span>',
    '<span className="text-slate-900">{option}</span>'
)

# Replace skills container styling
content = content.replace(
    '<div className="rounded-2xl border border-slate-200 p-4">',
    '<div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">'
)

# Replace skills heading styling
content = content.replace(
    '<p className="font-medium">Which skills do you have experience with?</p>',
    '<p className="font-medium text-slate-900">Which skills do you have experience with?</p>'
)

# Replace skills label styling
old_skill_label = '<label key={skill} className="inline-flex items-center gap-2 rounded-lg border px-3 py-2">'
new_skill_label = '<label key={skill} className={`inline-flex items-center gap-2 rounded-lg border px-3 py-2 cursor-pointer ${checked ? \'border-indigo-500 bg-indigo-50\' : \'border-slate-200 bg-white\'}`}>'
content = content.replace(old_skill_label, new_skill_label)

# Replace skills span styling  
old_skill_span = '<span>{skill}</span>'
new_skill_span = '<span className="text-slate-900">{skill}</span>'
# Only replace after the skills section - do this more carefully
lines = content.split('\n')
in_skills_section = False
for i, line in enumerate(lines):
    if 'Which skills do you have experience with?' in line:
        in_skills_section = True
    if in_skills_section and '<span>{skill}</span>' in line:
        lines[i] = line.replace('<span>{skill}</span>', '<span className="text-slate-900">{skill}</span>')

content = '\n'.join(lines)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed CSS styling for assessment questions and skills section")
