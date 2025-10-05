# Friday Demo Prep

## Principle

**Every Friday, you present the artifacts you delivered this week.**

This forces clarity, quality, and completeness. If you can't demo it on Friday, it wasn't done.

## Weekly Rhythm

### Monday Morning
- Review what shipped last week
- Plan this week's artifacts
- Define demo-able deliverables

### Tuesday-Thursday
- Build, test, commit
- Keep Friday demo in mind
- Ask: "Can I show this?"

### Friday Afternoon
- Demo completed work
- Gather feedback
- Tag releases
- Plan next week

## What Makes a Good Demo Artifact?

### ✅ Good Artifacts
- **Working code** with passing tests
- **Deployed feature** users can try
- **Documentation** that explains the value
- **Before/After comparison** showing improvement
- **Metrics** proving the change works

### ❌ Not Artifacts
- "I worked on X but it's not done"
- "Here's some code I wrote (untested)"
- "I was researching Y all week"
- "I started Z but hit blockers"
- PowerPoint presentations about future plans

## Demo Template

### 1. Context (30 seconds)

```
What: JavaScript Bridge for Replit Provider
Why:  Enable Python to execute Replit Extension APIs via Node.js
Who:  All Replit-based AICL workflows
```

### 2. Before State (30 seconds)

```
Before:
- No way to call Replit Extension APIs from Python
- Manual Node.js execution
- No error handling
```

### 3. What You Built (2 minutes)

```
Built:
- JSBridge class (providers/replit/js_bridge.py)
- Executes JavaScript via subprocess
- Parses JSON responses
- Timeout protection
- Retry logic with exponential backoff

Tests:
- 12 unit tests, all passing ✅
- 3 integration tests ✅
- Coverage: 89%

Tagged: v1.2.0-replit-bridge
```

### 4. Live Demo (2 minutes)

```python
# Show it working
from providers.replit.js_bridge import JavaScriptBridge

bridge = JavaScriptBridge()

# Demo 1: Simple execution
result = bridge.execute("""
const { init } = require('@replit/extensions');
(async () => {
    const dispose = await init();
    console.log(JSON.stringify({success: true}));
})();
""")

print(result.data)  # {'success': True}

# Demo 2: Error handling
result = bridge.execute("throw new Error('test')")
print(result.error)  # "Error: test"

# Demo 3: Timeout protection
result = bridge.execute("while(true){}", timeout=1)
print(result.error)  # "Execution timed out after 1s"
```

### 5. Impact (30 seconds)

```
Impact:
- Unblocks Replit provider implementation
- Foundation for 3 resource types
- 5+ future features depend on this

Next:
- Extension resource (next week)
- Authentication session (next week)
```

### 6. Q&A

```
Questions?
- Technical details
- Design decisions
- Future improvements
- Integration concerns
```

## Demo Preparation Checklist

### Thursday Night

```markdown
## Demo Prep for Friday

### Artifact
- [ ] Code is complete and merged
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Tagged with version

### Demo Environment
- [ ] Code runs locally
- [ ] Example data prepared
- [ ] Edge cases ready to show
- [ ] Backup plan if live demo fails

### Presentation
- [ ] Context slide ready
- [ ] Before/after comparison ready
- [ ] Key metrics ready
- [ ] Next steps identified

### Materials
- [ ] GitHub PR links
- [ ] Test results screenshot
- [ ] Coverage report
- [ ] Release notes
```

## Demo Formats

### Live Code Demo (Preferred)
```bash
# Terminal 1: Run the code
python demo/replit_bridge_demo.py

# Terminal 2: Show the tests
python -m pytest tests/providers/replit/test_js_bridge.py -v

# Terminal 3: Show coverage
python -m pytest --cov=providers.replit --cov-report=term-missing
```

### Video Recording (Backup)
```bash
# Record demo in advance (in case live fails)
asciinema rec friday_demo_replit_bridge.cast

# Show recording on Friday
asciinema play friday_demo_replit_bridge.cast
```

### Interactive Notebook (Alternative)
```python
# demo/replit_bridge_demo.ipynb
# Jupyter notebook with:
# - Setup
# - Examples
# - Edge cases
# - Performance metrics
```

## Common Demo Pitfalls

### ❌ Don't Do This

**The "Almost Done" Demo**
```
"I'm 90% done, just need to fix these tests..."
"It works on my machine, CI is just flaky..."
```
→ Not an artifact. Finish it or don't demo.

**The "Trust Me" Demo**
```
"Here's the code I wrote (doesn't run it)"
"The tests pass (doesn't show them)"
```
→ Show, don't tell. Run it live.

**The "Future Plans" Demo**
```
"Next week I'll build..."
"Eventually this will..."
```
→ Demo what's done, not what's planned.

**The "Reading Code" Demo**
```
*scrolls through 500 lines of code*
"So here's the implementation..."
```
→ Show behavior, not implementation.

## Demo Day Structure (Friday 3-4pm)

### 3:00 - 3:05: Week Recap
- What we committed to Monday
- What we delivered
- What we learned

### 3:05 - 3:45: Individual Demos
- Each person: 5-7 minutes
- Show working artifact
- Q&A

### 3:45 - 3:55: Metrics Review
- Lines of code delivered
- Tests added
- Coverage improvement
- Issues closed
- Tags created

### 3:55 - 4:00: Next Week Planning
- What's demoing next Friday?
- Dependencies identified
- Risks flagged

## Recording Demos

```bash
# Create demo recording directory
mkdir -p demos/2025-10-05/

# Record terminal session
asciinema rec demos/2025-10-05/replit-bridge-demo.cast

# Record screen
# (use QuickTime on Mac, OBS on Linux/Windows)

# Add to git
git add demos/2025-10-05/
git commit -m "docs: add Friday demo for Replit bridge"
```

## Demo Archive

Keep a log of all Friday demos:

```markdown
# demos/README.md

## 2025

### October 5, 2025
- **Replit Provider: JavaScript Bridge** (Zac)
  - [Recording](2025-10-05/replit-bridge-demo.cast)
  - [Code](https://github.com/org/repo/tree/v1.2.0-replit-bridge)
  - Tag: v1.2.0-replit-bridge

### September 28, 2025
- **OpenRouter Provider Improvements** (Zac)
  - [Recording](2025-09-28/openrouter-improvements.cast)
  - Tag: v1.1.5

...
```

## Success Metrics

- ✅ Every team member demos every Friday
- ✅ 100% of demos show working code
- ✅ All artifacts are tagged
- ✅ Demos take 5-7 minutes
- ✅ Recording saved for each demo
- ✅ Next week's artifacts defined

## Stakeholder Presentation

For broader audience (monthly):

```markdown
## Monthly Demo to Stakeholders

### Format
- 15 minutes total
- Top 3 features shipped this month
- Live demo of each
- Impact metrics
- Roadmap for next month

### Preparation
- Combine best Friday demos
- Add business context
- Show user impact
- Include success metrics

### Materials
- Demo recording
- Slides with metrics
- Release notes
- Customer feedback
```

## If You Have Nothing to Demo

**Don't skip. Instead:**

1. **Demo the blocker**
   - Show what's blocking you
   - Explain the problem
   - Ask for help

2. **Demo research/learning**
   - Show what you learned
   - Share documentation
   - Explain next steps

3. **Demo test improvements**
   - Show coverage gains
   - Demonstrate refactoring
   - Explain quality improvements

**But never say:** "I didn't do anything this week"

If truly nothing to show → reflect on process and fix for next week.