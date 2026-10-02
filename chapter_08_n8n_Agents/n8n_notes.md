# Chapter 8: n8n — Build Your Own Robots Without Writing Code

> A simple, step-by-step chapter on n8n for beginners.
> If you can use a computer and follow steps, you can learn this.

Our main example in this chapter is the workflow file in this folder:
[`04_SocialMediaPostGenerator.json`](./04_SocialMediaPostGenerator.json).
It is a small robot that writes a LinkedIn post, makes a picture for it, and posts it by itself every 3 days.

---

## How to Read This Chapter

- Read it from top to bottom the first time. Each part uses ideas from the part before it.
- Words in **bold** are important. You can find all of them in the [Glossary](#17-glossary) at the end.
- Boxes that start with **Tip** give you a useful trick.
- Boxes that start with **Careful** warn you about a common mistake.
- At the end there are [practice exercises](#18-practice-time) and a [quiz](#19-quick-quiz).

---

## Table of Contents

1. [What Is n8n?](#1-what-is-n8n)
2. [Why Use n8n?](#2-why-use-n8n)
3. [The Building Blocks (Key Words)](#3-the-building-blocks-key-words)
4. [How Data Moves in n8n](#4-how-data-moves-in-n8n)
5. [Setting Up n8n (Cloud and Local)](#5-setting-up-n8n-cloud-and-local)
6. [A Tour of the n8n Screen](#6-a-tour-of-the-n8n-screen)
7. [Types of Nodes](#7-types-of-nodes)
8. [Connections (The Lines Between Nodes)](#8-connections-the-lines-between-nodes)
9. [Expressions (Using Data from Earlier Nodes)](#9-expressions-using-data-from-earlier-nodes)
10. [Credentials (Keys to Your Accounts)](#10-credentials-keys-to-your-accounts)
11. [Build It Yourself: The Social Media Post Generator](#11-build-it-yourself-the-social-media-post-generator)
12. [Understanding the Workflow JSON File (Every Attribute)](#12-understanding-the-workflow-json-file-every-attribute)
13. [Export and Import](#13-export-and-import)
14. [Running, Testing and Fixing Workflows](#14-running-testing-and-fixing-workflows)
15. [Good Habits](#15-good-habits)
16. [Handy Keyboard Shortcuts](#16-handy-keyboard-shortcuts)
17. [Glossary](#17-glossary)
18. [Practice Time](#18-practice-time)
19. [Quick Quiz](#19-quick-quiz)
20. [Chapter Summary](#20-chapter-summary)

---

## 1. What Is n8n?

**n8n** (say it as "n-eight-n") is a tool that makes the computer do boring, repeated jobs for you, all by itself.

You build these jobs by joining boxes on the screen, a bit like joining Lego blocks. Most of the time you do not need to write any code.

- One complete job is called a **workflow**.
- Each box inside the workflow is called a **node**.

### A real-life example

Think about your school morning:

```text
Alarm rings  -->  Wake up  -->  Brush teeth  -->  Eat breakfast  -->  Catch the bus
```

- The **alarm** is what starts everything. In n8n this is called a **trigger**.
- Every step after the alarm is an **action**.
- The arrows show the **order** in which things happen.

An n8n workflow works exactly like this. Something starts it (a trigger), and then the steps (nodes) run one after another.

### Where does the name come from?

n8n is short for **"nodemation"** (node + automation).
Take the word **n**odematio**n**: it starts with "n", ends with "n", and has **8** letters in the middle. So: **n-8-n**.

### What can n8n do? Some examples

| When this happens... | ...n8n does this |
|---|---|
| Every morning at 7 AM | Checks the weather and sends it to your phone. |
| Someone fills a form on your website | Saves the answer in Google Sheets and sends a thank-you email. |
| A new bug is created in Jira | Asks AI to write test cases for it. |
| Every 3 days at 10 AM | Asks AI to write a LinkedIn post with a picture and posts it. **(Our example!)** |

### Quick facts

| Question | Answer |
|---|---|
| What type of tool is it? | A **workflow automation** tool. |
| Who makes it? | A company called n8n, started in Berlin, Germany, in 2019. |
| Do I need to code? | No. But you **can** add code (JavaScript or Python) when you want. |
| How many apps can it talk to? | Hundreds (400+), like Gmail, Slack, Jira, LinkedIn, Google Sheets, OpenAI and many more. |
| Where does it run? | On n8n's computers (**Cloud**) or on your own computer (**Local / Self-hosted**). |
| Is it free? | Running it on your own computer (Community Edition) is free. Cloud is paid, with a free trial. |
| What is its license? | "Fair-code" (Sustainable Use License). The code is public and you can use it for yourself or your company's own work. You cannot sell n8n itself as your own service. |

---

## 2. Why Use n8n?

### Doing it by hand vs letting n8n do it

| Doing it by hand | With n8n |
|---|---|
| You must remember to do the job. | It runs on time, every time. |
| Copy-paste between apps takes long. | Apps talk to each other directly. |
| Easy to make small mistakes. | Same steps, same way, every time. |
| You get bored doing it again and again. | The robot never gets bored. |

### n8n vs other ways

| Option | What it is like |
|---|---|
| **n8n** | Visual boxes and lines. Can run on your own computer for free. Strong AI features. You can add code when needed. |
| **Zapier / Make** | Also visual tools. Only run on their cloud. Often cost more for big jobs. |
| **Writing a full program** | Most control, but you must write and look after all the code yourself. |

> **Tip:** In this repository, Chapter 3 and Chapter 7 build AI tools by writing Python code. Chapter 8 builds similar AI tools in n8n by joining boxes. Comparing them is a great way to learn.

---

## 3. The Building Blocks (Key Words)

Learn these words first. Everything else in this chapter uses them.

| Word | Simple meaning | Real-life picture |
|---|---|---|
| **Workflow** | One complete automatic job, made of nodes joined by lines. | A recipe. |
| **Node** | One box = one step in the job. | One line in the recipe, like "boil water". |
| **Trigger node** | The first node. It decides **when** the workflow starts. | The alarm clock. |
| **Action node** | A node that **does** something (send email, call AI, create a post). | Your hands doing the work. |
| **Connection** | The line between two nodes. Data travels along it. | A conveyor belt. |
| **Canvas** | The big empty board where you place nodes. | Your drawing sheet. |
| **Execution** | One run of the workflow, from start to end. | Cooking the recipe once. |
| **Item** | One piece of data that moves between nodes. | One lunch box on the conveyor belt. |
| **Credential** | Saved login details (like an API key) so n8n can use your accounts. | A key to a locked door. |
| **Expression** | A small formula inside `{{ }}` that picks data from earlier nodes. | "Use the answer from step 2 here." |
| **Active / Published** | When ON, the workflow runs by itself whenever its trigger fires. | Switching the robot ON. |

---

## 4. How Data Moves in n8n

### Items: lunch boxes on a conveyor belt

Imagine a factory conveyor belt. Lunch boxes move from one machine to the next. Each machine opens the box, does something, and passes it on.

In n8n:

- The **lunch boxes** are called **items**.
- The **machines** are the **nodes**.
- The **conveyor belt** is the **connection** (the line).

```text
 [Node A] ===( item )===> [Node B] ===( item )===> [Node C]
```

### What is inside an item? (JSON)

n8n stores the data inside each item in a format called **JSON** (say "jay-son").
JSON is just a neat way to write information as **name: value** pairs.

```json
{
  "topic": "Why AI-generated Playwright tests can pass and still test nothing",
  "content_pillar": "Playwright",
  "suggested_platform": "LinkedIn"
}
```

### JSON in 1 minute

| Symbol | Meaning | Example |
|---|---|---|
| `{ }` | An **object**: a group of name-value pairs. | `{ "name": "Riya", "age": 13 }` |
| `"name": value` | One **pair**. The name is always in double quotes. | `"city": "Delhi"` |
| `" "` | A **string** (text). | `"hello"` |
| `13`, `4.5` | A **number** (no quotes). | `"marks": 95` |
| `true` / `false` | A **yes / no** value (called a boolean). | `"passed": true` |
| `[ ]` | A **list** (also called an array). | `"subjects": ["Maths", "Science"]` |
| `null` | "Nothing here" / empty. | `"middleName": null` |

### The full shape of items

When data leaves a node, n8n sends a **list of items**. Each item has a `json` part, and sometimes a `binary` part:

```json
[
  {
    "json":   { "post_title": "Testing AI output" },
    "binary": { "data": "(an image file lives here)" }
  }
]
```

- **`json`** = normal data (text, numbers, true/false).
- **`binary`** = **files**, like pictures, PDFs or audio. In our example, the AI-made image travels in `binary`.

### One important rule

> Most nodes run **once for every item** they receive.
> If 5 items come in, the node does its job 5 times. If 1 item comes in, it runs 1 time.

Our Social Media Post Generator always works with **1 item**, so every node runs once.

---

## 5. Setting Up n8n (Cloud and Local)

There are two main ways to use n8n:

| Way | Real-life picture | In short |
|---|---|---|
| **n8n Cloud** | Eating at a restaurant. Someone else cooks and cleans. | n8n runs it for you on the internet. You pay monthly. |
| **Local / Self-hosted** | Cooking at home. You do the work, but it is free. | You run n8n on your own computer or server. |

### 5.1 Option A — n8n Cloud (easiest)

1. Go to **https://n8n.io** and click **Get started** (or **Sign up**).
2. Enter your email, name and a password. Verify your email.
3. Choose a name for your workspace. Your n8n address will look like
   `https://your-name.app.n8n.cloud`
4. You get a **free trial** (usually 14 days). After that you pick a paid plan.
   Plans and prices change, so check **https://n8n.io/pricing**.
5. You land on the **Overview** page. You are ready to build.

**Good things**
- Nothing to install.
- It runs 24x7, even when your laptop is off. (Very useful for our workflow that posts every 3 days!)
- Webhooks (web links that start workflows) work from the internet straight away.
- Updates happen for you.
- Some apps can be connected with an easy **"Connect my account"** button.

**Not-so-good things**
- It costs money after the trial.
- Your data is stored on n8n's servers.
- There is a limit on how many runs you get per month, depending on your plan.

### 5.2 Option B — Local with Node.js (`npx`)

This is the quickest local way if you already use Node.js.

**Step 1: Install Node.js**
- Download the **LTS** version from **https://nodejs.org** and install it.
- Check it worked. Open a terminal and type:

```bash
node -v
npm -v
```

You should see version numbers. (Check the n8n docs for which Node.js versions are supported.)

**Step 2: Start n8n**

```bash
npx n8n
```

This downloads n8n and starts it. The first time takes a few minutes.

Or, install it for good and start it any time:

```bash
npm install n8n -g
n8n start
```

**Step 3: Open it in your browser**

Go to: **http://localhost:5678**

- `localhost` means "this computer".
- `5678` is the **port** (like a door number) that n8n uses.

**Step 4: Create the owner account**

The first time, n8n asks for an email, name and password. This account lives **only on your computer**.

**Step 5: Stop it**

Go back to the terminal and press **Ctrl + C**.

**Where is my data saved?**
In a hidden folder called **`.n8n`** inside your home folder (`~/.n8n`). It holds your workflows, saved credentials and the secret **encryption key**.

> **Careful:** Do not delete the `~/.n8n` folder. You would lose all your workflows and credentials.

**To update n8n later:**

```bash
npm update -g n8n
```

### 5.3 Option C — Local with Docker (recommended for local)

**Docker** is a tool that packs an app together with everything it needs into one sealed box called a **container**. You do not need to install Node.js for this.

**Step 1:** Install **Docker Desktop** from **https://www.docker.com** and open it.

**Step 2:** Run these two commands in the terminal:

```bash
docker volume create n8n_data

docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
```

**What does each part mean?**

| Part | Meaning |
|---|---|
| `docker volume create n8n_data` | Make a safe storage box called `n8n_data` so your work is not lost. |
| `docker run` | Start a container. |
| `-it` | Show the output in the terminal and let you stop it with Ctrl + C. |
| `--rm` | Throw away the container when it stops. (Your work is still safe in the volume.) |
| `--name n8n` | Give the container the name `n8n`. |
| `-p 5678:5678` | Connect door 5678 on your computer to door 5678 in the container. |
| `-v n8n_data:/home/node/.n8n` | Save n8n's data into the `n8n_data` storage box. |
| `docker.n8n.io/n8nio/n8n` | The official n8n image (the "box" to run). |

**Step 3:** Open **http://localhost:5678** and create your owner account.

**Set your time zone (important for Schedule Triggers!)**

If you skip this, "10 AM" may mean 10 AM in a different country. Add your time zone like this (example for India):

```bash
docker run -it --rm --name n8n -p 5678:5678 \
  -e GENERIC_TIMEZONE="Asia/Kolkata" \
  -e TZ="Asia/Kolkata" \
  -v n8n_data:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n
```

**Run it in the background with Docker Compose (optional)**

Create a file named `docker-compose.yml`:

```yaml
services:
  n8n:
    image: docker.n8n.io/n8nio/n8n
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - GENERIC_TIMEZONE=Asia/Kolkata
      - TZ=Asia/Kolkata
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

Then use:

```bash
docker compose up -d     # start in the background
docker compose down      # stop
docker compose pull      # download the newest n8n (then run "up -d" again)
```

### 5.4 Useful settings for local n8n (environment variables)

**Environment variables** are settings you give to n8n when it starts.

| Setting | What it does | Example |
|---|---|---|
| `GENERIC_TIMEZONE` | Time zone used by the Schedule Trigger. | `Asia/Kolkata` |
| `TZ` | Time zone of the computer inside the container. | `Asia/Kolkata` |
| `N8N_PORT` | Change the door number from 5678 to something else. | `5679` |
| `WEBHOOK_URL` | The public web address of your n8n (needed for webhooks from the internet). | `https://my-tunnel.example.com/` |
| `N8N_ENCRYPTION_KEY` | The secret key used to lock your saved credentials. Keep it safe and never share it. | (a long random text) |

### 5.5 Special problems with local n8n (and how to fix them)

| Problem | Why it happens | Fix |
|---|---|---|
| The Schedule Trigger did not run. | Your laptop was off or asleep, or n8n was not running. | Keep n8n running, use a small always-on server, or use n8n Cloud. |
| It ran at the wrong time. | Time zone not set. | Set `GENERIC_TIMEZONE`, or set the time zone in the workflow's **Settings**. |
| Websites cannot reach my Webhook. | `localhost` only works on your own computer. | Use a tunnel tool such as **ngrok** or **cloudflared**, and set `WEBHOOK_URL`. |
| n8n in Docker cannot reach Ollama on my computer. | Inside Docker, `localhost` means the container, not your computer. | Use `http://host.docker.internal:11434` as the Ollama address. |
| LinkedIn/Google login fails. | These use **OAuth**, which needs a "redirect URL". | Copy the **OAuth Redirect URL** shown in the n8n credential window into your LinkedIn/Google developer app. |

> **Good news:** The Schedule Trigger, the Manual Trigger and the chat window inside the editor all work fine on local n8n without any tunnel.

### 5.6 Cloud vs Local — side by side

| Point | n8n Cloud | Local / Self-hosted |
|---|---|---|
| Setup | Sign up and go. | Install Node.js or Docker. |
| Cost | Paid (free trial first). | Free (Community Edition). |
| Runs when laptop is off? | Yes. | No (unless you use a server). |
| Webhooks from the internet | Work straight away. | Need a tunnel or a public server. |
| Updates | Automatic. | You update it yourself. |
| Your data | Stored by n8n. | Stays on your computer. |
| Use local AI (Ollama) | Hard. | Easy. |
| Best for | Beginners, always-on jobs. | Learning for free, privacy, local AI. |

> **Which one should I pick?**
> To learn fast: start with the Cloud free trial.
> To learn for free and keep data private: use Docker locally.
> For our Social Media Post Generator (posts every 3 days), Cloud or an always-on server is best, because your laptop might be off.

---

## 6. A Tour of the n8n Screen

Buttons can have slightly different names in different versions of n8n. The ideas stay the same.

### 6.1 The left sidebar

| Item | What it is for |
|---|---|
| **Overview** | Home page. Has tabs for **Workflows**, **Credentials** and **Executions**. |
| **Templates** | Ready-made workflows made by other people. Copy one and change it. |
| **Settings** | Your account, users, API keys, community nodes and more. |
| **Help** | Docs, forum, and "What's new". |

### 6.2 The workflow editor

```text
+--------------------------------------------------------------------------+
|  Workflow name   [tags]          Editor | Executions    [Save] [Active] ...|  <- Top bar
+--------------------------------------------------------------------------+
|                                                                       [+]|  <- Open nodes panel
|                                                                          |
|        [Trigger] -----> [Node] -----> [Node]                             |  <- Canvas
|                                                                          |
|                                                                          |
|                       [ Execute workflow ]                               |  <- Run button
+--------------------------------------------------------------------------+
|  Logs (what happened in the last run)                                    |  <- Logs panel
+--------------------------------------------------------------------------+
```

| Part | What it does |
|---|---|
| **Workflow name** | Click it to rename your workflow. |
| **Tags** | Labels like "AI" or "LinkedIn" to keep things organised. |
| **Editor / Executions tabs** | Editor = build. Executions = see past runs of this workflow. |
| **Save** | Saves your work (also Ctrl/Cmd + S). |
| **Active / Publish** | Turns the workflow ON so it runs by itself. Older versions show an **Active** switch; newer versions show a **Publish** button. |
| **... (three dots) menu** | Download, Import from File, Import from URL, Duplicate, Settings, Delete and more. |
| **+ button** | Opens the **nodes panel** where you search and add nodes. |
| **Canvas** | Where your nodes and lines live. Scroll to zoom, drag to move around. |
| **Execute workflow** | Runs the whole workflow right now to test it. (Older versions: "Test workflow".) |
| **Logs panel** | Shows each node's input and output for the last run. |

### 6.3 Inside a node (the node window)

Double-click any node to open it. You will see three parts:

```text
+----------------+------------------------------+----------------+
|     INPUT      |   PARAMETERS  |  SETTINGS    |     OUTPUT     |
|                |                              |                |
| Data coming in | The fields you fill in       | Data going out |
| from the node  | (what this node should do)   | after this     |
| before         |                              | node runs      |
|                |      [ Execute step ]        |                |
+----------------+------------------------------+----------------+
```

- **Input (left):** the data that came from the previous node.
- **Parameters (middle):** the main fields you fill in.
- **Settings (middle, second tab):** extra behaviour (see below).
- **Output (right):** the result after this node runs.
- **Execute step:** runs only up to this node, so you can test it. (Older versions: "Test step".)

You can view input and output data in three ways:

| View | Best for |
|---|---|
| **Schema** | Seeing the names of the fields. You can **drag** a field from here into a parameter. |
| **Table** | Seeing many items like a spreadsheet. |
| **JSON** | Seeing the exact raw data. |

### 6.4 The node Settings tab

| Setting | What it does |
|---|---|
| **Always Output Data** | Pass on an empty item even if this node finds nothing, so the workflow keeps going. |
| **Execute Once** | Run only for the first item, even if many items come in. |
| **Retry On Fail** | If the node fails (for example, the internet blips), try again a few times. |
| **On Error** | What to do if this node fails: **Stop Workflow**, **Continue**, or **Continue (using error output)**. |
| **Notes** | Write a note about this node. You can show it on the canvas. |

---

## 7. Types of Nodes

There are hundreds of nodes, but they fit into a few groups.

### 7.1 Trigger nodes (how a workflow starts)

| Trigger | Starts the workflow when... |
|---|---|
| **Manual Trigger** ("When clicking 'Execute workflow'") | You click the button. Great for testing. |
| **Schedule Trigger** | A time arrives (every hour, every day at 9 AM, every 3 days at 10 AM...). **Used in our example.** |
| **Webhook** | Another app or website sends a message to a special n8n web link. |
| **Form Trigger** | Someone fills in a simple form that n8n creates for you. |
| **Chat Trigger** ("When chat message received") | Someone types a message in a chat box. Used in this folder's Jira workflows. |
| **App triggers** (Gmail Trigger, Jira Trigger, ...) | Something happens in an app, like a new email or a new Jira issue. |
| **Error Trigger** | Another workflow fails. Used to send you an alert. |
| **Execute Workflow Trigger** ("When executed by another workflow") | Another workflow calls this one. |

> **Webhook: Test URL vs Production URL**
> A Webhook node has two links.
> The **Test URL** works only while you are testing in the editor.
> The **Production URL** works only when the workflow is **Active / Published**.

### 7.2 App (action) nodes

These nodes talk to apps. Each app has many **actions**, like "Create a post" or "Get an issue".

| Node | Example actions |
|---|---|
| **LinkedIn** | Create a post. **(Used in our example.)** |
| **Jira Software** | Get an issue, create an issue, update an issue. |
| **Gmail** | Send an email, read emails. |
| **Slack / Telegram** | Send a message. |
| **Google Sheets** | Add a row, read rows, update a row. |
| **OpenAI** | Write text, **generate an image** (used in our example), make audio. |
| **HTTP Request** | Talk to **any** website or API, even if n8n has no special node for it. Think of it as a universal remote. |

### 7.3 Logic and data nodes (the "thinking" helpers)

| Node | What it does | Real-life picture |
|---|---|---|
| **If** | Checks a condition and sends data to **true** or **false**. | "If it is raining, take an umbrella." |
| **Switch** | Like If, but with many paths. | A railway track switch. |
| **Merge** | Joins data from two paths into one. **(Used in our example.)** | Two rivers joining. |
| **Filter** | Keeps only the items that match a rule. | A sieve. |
| **Edit Fields (Set)** | Adds, changes or removes fields. | Rewriting a label on a box. |
| **Code** | Runs your own JavaScript or Python. | Your secret tool. |
| **Wait** | Pauses for some time, or until something happens. | A pause button. |
| **Loop Over Items** | Handles items in small groups, one group at a time. | Serving a queue one by one. |
| **Split Out** | Turns one list into many separate items. | Opening a pack of pencils. |
| **Aggregate** | Joins many items into one list. | Putting pencils back in the box. |
| **Remove Duplicates** | Removes repeated items. | Removing double entries. |
| **Execute Workflow** | Calls another workflow (a **sub-workflow**). | Asking a friend to do part of the job. |
| **No Operation** | Does nothing. Useful as a placeholder. | An empty chair. |

### 7.4 AI nodes

n8n has special nodes for AI. They work as a team: one **main (root) node** and some **helper (sub) nodes** plugged into it.

| AI node | Job | Real-life picture |
|---|---|---|
| **AI Agent** (root) | Thinks, decides, and can use tools to finish a task. **(Used twice in our example.)** | A student solving a problem. |
| **Basic LLM Chain** (root) | Asks the AI one question and gets one answer. No tools. | Asking a question and getting a reply. |
| **Chat Model** (sub) — OpenAI, Groq, Ollama, Anthropic, Gemini... | The actual AI "brain" that writes the text. | The student's brain. |
| **Memory** (sub) — e.g. Simple Memory | Remembers the last few messages in a chat. | A notebook. |
| **Tool** (sub) — e.g. Jira Tool, HTTP Request Tool, Calculator | Things the agent is allowed to use. | A calculator or a phone. |
| **Output Parser** (sub) — e.g. Structured Output Parser | Forces the AI's answer into a fixed shape (fixed fields). **(Used in our example.)** | A printed answer sheet with boxes to fill. |

**AI Agent vs Basic LLM Chain**

| AI Agent | Basic LLM Chain |
|---|---|
| Can use tools (Jira, web search, calculator...). | No tools. |
| Can have memory. | No memory. |
| Can think in several steps. | One question, one answer. |
| Good for chat bots and tasks needing actions. | Good for simple "write this / summarise this". |

> In our example, the agents use **no tools and no memory**, so a Basic LLM Chain could also do the job. Using an AI Agent makes it easy to add tools later.

### 7.5 Sticky Notes

A **Sticky Note** is not a real working node. It is a coloured note on the canvas to explain or group nodes. Our example has three: **Trigger**, **Actions** and **Results**.

---

## 8. Connections (The Lines Between Nodes)

### 8.1 Main connections (solid lines)

- These carry **items** from one node to the next.
- Data flows from the **right side (output)** of one node into the **left side (input)** of the next.

```text
[Schedule Trigger] ---> [Content Topic Generator] ---> [Content creator]
```

### 8.2 AI connections (dashed lines under AI nodes)

An AI Agent has small sockets at the **bottom**. Helper nodes plug into them.

```text
                [ AI Agent ]
               /     |      \       \
     Chat Model   Memory   Tool   Output Parser
```

| Socket name | JSON name | What plugs in |
|---|---|---|
| Chat Model | `ai_languageModel` | The AI brain (OpenAI, Groq, Ollama...). **Required.** |
| Memory | `ai_memory` | Simple Memory and others. |
| Tool | `ai_tool` | Jira Tool, HTTP Request Tool, etc. You can add many. |
| Output Parser | `ai_outputParser` | Structured Output Parser. Appears when **Require Specific Output Format** is ON. |

### 8.3 Many inputs and many outputs

- **One output to many nodes:** the data is copied to each one. In our example, the **Content creator** sends its result to **both** "Generate an image" and "Merge".
- **Nodes with many outputs:** the **If** node has two outputs: **true** and **false**.
- **Nodes with many inputs:** the **Merge** node has **Input 1** and **Input 2**.

---

## 9. Expressions (Using Data from Earlier Nodes)

### 9.1 Fixed vs Expression

Every field in a node can be:

- **Fixed:** plain text you type. It is the same every time.
- **Expression:** a small formula that changes based on the data. You write it inside **double curly brackets** `{{ }}`.

Example:

```text
Fixed:       Hello friend
Expression:  Hello {{ $json.name }}
```

If the incoming item has `"name": "Aman"`, the expression becomes **Hello Aman**.

> **Tip:** The easiest way to make an expression is to **drag** a field from the **Input** panel (left side) and **drop** it into a parameter. n8n writes the expression for you.

### 9.2 The most useful expression words

| Expression | Meaning | Example result |
|---|---|---|
| `{{ $json.topic }}` | The `topic` field from the item coming **into** this node. | `Why AI tests can lie` |
| `{{ $json.output.topic }}` | The `topic` field inside `output`. | (same idea, one level deeper) |
| `{{ $('Schedule Trigger').item.json.timestamp }}` | A field from **any** earlier node, picked by its name. | `2026-10-02T10:00:00...` |
| `{{ $now }}` | The date and time right now. | `2026-10-02T10:00:00.000+05:30` |
| `{{ $today }}` | Today's date at midnight. | `2026-10-02T00:00:00...` |
| `{{ $now.toFormat('dd-MM-yyyy') }}` | Today's date in your own format. | `02-10-2026` |
| `{{ $json.name.toUpperCase() }}` | Make text CAPITAL letters. | `AMAN` |
| `{{ $json.price * 2 }}` | Do maths. | `200` |
| `{{ $execution.id }}` | The ID number of this run. | `1234` |
| `{{ $workflow.name }}` | The name of this workflow. | `04_SocialMediaPostGenerator` |
| `{{ $fromAI('Issue_Key', '', 'string') }}` | Lets the **AI Agent fill this field by itself** (only in tool nodes). | `KAN-1` |

### 9.3 Expressions in our example

In the **Content creator ( LinkedIn Post )** node, the prompt is:

```text
Write me a linkedIn Post.

Topic :  {{ $json.output.topic }}
Angle : {{ $json.output.angle }}
Audience : {{ $json.output.target_reader }}
```

This means: "Take the topic, angle and audience that the **Content Topic Generator** just made, and put them into this prompt."

In the **Content Topic Generator**, the prompt ends with:

```text
Execution date:
{{ $now }}
```

Adding the date makes each run's prompt a little different. This helps the AI give a **fresh** topic each time.

> **Careful:** `$json` means the data from the node **directly before** this one.
> To use data from a node further back, use `$('Node Name')`, like
> `{{ $('Content Topic Generator').item.json.output.topic }}`.

---

## 10. Credentials (Keys to Your Accounts)

### 10.1 What is a credential?

A **credential** is your saved login for an app, such as an **API key** or an account login. n8n uses it to work with that app for you.

> Think of it as a key you give to a trusted helper. The helper can open the door, but nobody else can see the key.

### 10.2 Why are credentials kept separate from the workflow?

- Your secret keys are stored **locked (encrypted)** inside n8n.
- When you **export** a workflow, the secret keys are **not** included. Only the credential's **name** and **ID** are saved.
- So you can share workflow files safely (but see the safety check in [Section 13.7](#137-safety-check-before-you-share-a-json-file)).

### 10.3 How to add a credential

**Way 1:** Overview -> **Credentials** tab -> **Add credential** -> search for the app -> fill in the details -> **Save**.

**Way 2 (easier):** Open a node -> in the **Credential** field choose **Create new credential** -> fill it in -> **Save**.

n8n tests the credential when you save it. A green message means it works.

### 10.4 Types of credentials

| Type | How it works | Examples |
|---|---|---|
| **API key** | You copy a long secret text from the app's website and paste it into n8n. | OpenAI, Groq |
| **OAuth2** | You click **Sign in with...** and log in through a pop-up window. No key to copy. | LinkedIn, Google, Slack |
| **Email + API token** | You give your account email, a token and your site address. | Jira Software Cloud |
| **Local address** | You give the address of a program on your computer. | Ollama (`http://localhost:11434`) |

### 10.5 Credentials used in our example

| Node | Credential | Notes |
|---|---|---|
| OpenAI Chat Model, OpenAI Chat Model1, Generate an image | OpenAI | Get an API key from **platform.openai.com**. Using the OpenAI API costs money per use. |
| Create a post | LinkedIn (OAuth2) | On n8n Cloud you may get a simple "Connect my account" button. On local n8n you need your own LinkedIn developer app (see below). |

**LinkedIn on local n8n (short version)**

1. Go to **https://developer.linkedin.com** and create an app.
2. In the app, add the products **Share on LinkedIn** and **Sign In with LinkedIn using OpenID Connect**.
3. Copy the **Client ID** and **Client Secret** into the n8n LinkedIn credential.
4. Copy n8n's **OAuth Redirect URL** (shown in the credential window) into the LinkedIn app's **Authorized redirect URLs**.
5. Click **Connect** in n8n and log in.

---

## 11. Build It Yourself: The Social Media Post Generator

Now let us build the full example, step by step.
File: [`04_SocialMediaPostGenerator.json`](./04_SocialMediaPostGenerator.json)

### 11.1 What does it do? (The story)

> Every 3 days at 10 AM, the robot wakes up.
> First, an AI **thinks of a topic** about software testing and AI.
> Then a second AI **writes a LinkedIn post** about that topic, plus a description for a picture.
> Then a third AI tool **draws the picture**.
> The text and the picture are **joined together**.
> Finally, the robot **posts it on LinkedIn**.

### 11.2 The picture of the workflow

```text
 +--------------------+
 |  Schedule Trigger  |   every 3 days, at 10 AM
 +---------+----------+
           |
           v
 +---------------------------+     <-- OpenAI Chat Model (gpt-5-mini)
 |  Content Topic Generator  |     <-- Structured Output Parser (topic fields)
 |        (AI Agent)         |
 +---------+-----------------+
           |
           v
 +-----------------------------------+     <-- OpenAI Chat Model1 (gpt-5-mini)
 | Content creator ( LinkedIn Post ) |     <-- Structured Output Parser1 (post fields)
 |            (AI Agent)             |
 +---------+---------------+---------+
           |               |
           v               |
 +-------------------+     |
 | Generate an image |     |   (OpenAI, gpt-image-2)
 +---------+---------+     |
           |               |
           v Input 1       v Input 2
        +--------------------+
        |       Merge        |   joins picture + text
        +---------+----------+
                  |
                  v
        +--------------------+
        |   Create a post    |   (LinkedIn)
        +--------------------+
```

### 11.3 All the nodes in this workflow

There are **13** nodes: **10 working nodes** and **3 sticky notes**.

| # | Node name | Node type | Its job |
|---|---|---|---|
| 1 | Sticky Note | Sticky Note | Label: "Trigger". |
| 2 | Sticky Note1 | Sticky Note | Label: "Actions". |
| 3 | Sticky Note2 | Sticky Note | Label: "Results". |
| 4 | Schedule Trigger | Schedule Trigger | Starts the workflow every 3 days at 10 AM. |
| 5 | Content Topic Generator | AI Agent | Thinks of one fresh topic. |
| 6 | OpenAI Chat Model | OpenAI Chat Model | The brain for node 5. |
| 7 | Structured Output Parser | Structured Output Parser | Makes node 5 answer in 8 fixed fields. |
| 8 | Content creator ( LinkedIn Post ) | AI Agent | Writes the post. |
| 9 | OpenAI Chat Model1 | OpenAI Chat Model | The brain for node 8. |
| 10 | Structured Output Parser1 | Structured Output Parser | Makes node 8 answer in 4 fixed fields. |
| 11 | Generate an image | OpenAI | Draws the picture. |
| 12 | Merge | Merge | Joins the text and the picture. |
| 13 | Create a post | LinkedIn | Posts on LinkedIn. |

### 11.4 Before you start

- [ ] n8n is running (Cloud or Local).
- [ ] You have an **OpenAI** credential (or n8n Cloud's built-in AI credits, if your plan offers them).
- [ ] You have a **LinkedIn** credential.
- [ ] You have about 30-45 minutes.

### Step 1 — Create a new workflow

1. On the Overview page, click **Create Workflow**.
2. Click the name at the top and rename it to **04_SocialMediaPostGenerator**.
3. Press **Ctrl/Cmd + S** to save.

### Step 2 — Add the Schedule Trigger

1. Click **Add first step** (or the **+** button).
2. Search for **Schedule** and pick **Schedule Trigger**.
3. Fill in:

| Field | Value |
|---|---|
| Trigger Interval | **Days** |
| Days Between Triggers | **3** |
| Trigger at Hour | **10am** |
| Trigger at Minute | **0** |

> **Tip:** You do not have to wait 3 days to test! Clicking **Execute workflow** runs it right now.

### Step 3 — Add the first AI Agent: "Content Topic Generator"

1. Click the **+** on the right side of the Schedule Trigger.
2. Search for **AI Agent** and add it.
3. Rename it (press **F2**, or click the name) to **Content Topic Generator**.
4. Fill in:

| Field | Value |
|---|---|
| Source for Prompt (User Message) | **Define below** |
| Prompt (User Message) | The request (see below). Switch the field to **Expression** because it uses `{{ $now }}`. |
| Require Specific Output Format | **ON** (this adds the Output Parser socket) |
| Options -> Add Option -> **System Message** | The long rules text (see below). |

**User message (short version — the full text is in the JSON file):**

```text
Generate ONE fresh, specific content topic for my Software Testing / QA / AI-in-QA personal brand.
...
Avoid generic topics.
Do not write the full post.
Follow the System Message rules and return the output using the required structured schema exactly.

Execution date:
{{ $now }}
```

**System message (short version):**

```text
You are a senior content strategist specializing in Software Testing, Quality Engineering,
Test Automation, and practical AI usage in QA.
Your task is to generate ONE fresh, specific, technically credible content topic...
(preferred areas, quality rules, good/bad examples, guardrails, output format)
```

**System message vs User message — what is the difference?**

| System message | User message (prompt) |
|---|---|
| The **rules of the game**. Who the AI should act as, and what it must and must not do. | The **actual task** for this run. |
| Like a teacher's instructions written on the board before the exam. | Like the exam question itself. |
| Example: "Do NOT invent statistics." | Example: "Generate ONE fresh topic." |

### Step 4 — Plug in the Chat Model (the brain)

1. Under the agent, click the **+** below **Chat Model**.
2. Choose **OpenAI Chat Model**.
3. Pick your OpenAI credential.
4. **Model:** `gpt-5-mini`.

### Step 5 — Plug in the Structured Output Parser (the answer sheet)

1. Click the **+** below **Output Parser**.
2. Choose **Structured Output Parser**.
3. **Schema Type:** **Define using JSON Schema**.
4. Paste this schema:

```json
{
  "type": "object",
  "properties": {
    "topic":               { "type": "string" },
    "content_pillar":      { "type": "string" },
    "angle":               { "type": "string" },
    "target_reader":       { "type": "string" },
    "engineering_problem": { "type": "string" },
    "key_takeaway":        { "type": "string" },
    "hook_direction":      { "type": "string" },
    "suggested_platform":  { "type": "string" }
  },
  "required": [
    "topic", "content_pillar", "angle", "target_reader",
    "engineering_problem", "key_takeaway", "hook_direction", "suggested_platform"
  ]
}
```

**What is a schema?** It is a blank form that the AI **must** fill in.

| Schema word | Meaning |
|---|---|
| `"type": "object"` | The answer must be a `{ }` group of fields. |
| `"properties"` | The list of fields (boxes) in the form. |
| `"type": "string"` | That box must contain text. |
| `"required"` | These boxes can never be left empty. |

> **Easier option:** Choose **Schema Type: Generate From JSON Example** and just paste an example answer. n8n works out the schema for you.

**Why do we need this?** Without it, the AI might reply with a long paragraph. With it, the answer always has the same fields, so the next node can use `{{ $json.output.topic }}` safely.

### Step 6 — Test the first agent

1. Open the **Content Topic Generator** node.
2. Click **Execute step**.
3. Look at the **Output**. It will look something like this (your result will be different):

```json
{
  "output": {
    "topic": "Why AI-generated Playwright tests can pass and still test nothing",
    "content_pillar": "Playwright",
    "angle": "AI can write tests that run green but check nothing important.",
    "target_reader": "Automation engineers using AI to write Playwright tests",
    "engineering_problem": "Tests without strong assertions give false confidence.",
    "key_takeaway": "Always review what an AI-generated test actually asserts.",
    "hook_direction": "Start with a green test run that hides a real bug.",
    "suggested_platform": "LinkedIn"
  }
}
```

Notice: the agent puts the answer inside a field called **`output`**. That is why later nodes use `$json.output.something`.

### Step 7 — Add the second AI Agent: "Content creator ( LinkedIn Post )"

1. Click **+** after the Content Topic Generator and add another **AI Agent**.
2. Rename it to **Content creator ( LinkedIn Post )**.
3. Fill in:

| Field | Value |
|---|---|
| Source for Prompt (User Message) | **Define below** |
| Prompt (User Message) | See below (an **Expression**). |
| Require Specific Output Format | **ON** |
| Options -> System Message | `You write a linkedIn post for the software testing audience. Return only the fields required by the schema.` |

**Prompt:**

```text
Write me a linkedIn Post.

Topic :  {{ $json.output.topic }}
Angle : {{ $json.output.angle }}
Audience : {{ $json.output.target_reader }}

Rules: no contractions, no emojis, plain declarative sentences, short paragraphs,
one clear takeaway, 150–250 words. Also produce a post title and a one-sentence
image prompt describing a clean technical illustration for this post.
```

> **Tip:** Instead of typing `{{ $json.output.topic }}`, drag the **topic** field from the Input panel and drop it into the prompt.

### Step 8 — Give the second agent its brain and answer sheet

1. **Chat Model:** add **OpenAI Chat Model** (it will be named "OpenAI Chat Model1"), model `gpt-5-mini`.
2. **Output Parser:** add **Structured Output Parser** (named "Structured Output Parser1") with this schema:

```json
{
  "type": "object",
  "properties": {
    "post_title":   { "type": "string" },
    "post_body":    { "type": "string" },
    "hashtags":     { "type": "string" },
    "image_prompt": { "type": "string" }
  },
  "required": ["post_title", "post_body", "hashtags", "image_prompt"]
}
```

Test it with **Execute step**. The output will have `output.post_title`, `output.post_body`, `output.hashtags` and `output.image_prompt`.

### Step 9 — Generate the image

1. Click **+** after the Content creator, search **OpenAI**, and choose the action **Generate an image**.
2. Fill in:

| Field | Value |
|---|---|
| Credential | Your OpenAI credential |
| Resource | **Image** |
| Operation | **Generate an Image** |
| Model | `gpt-image-2` |
| Prompt (Expression) | See below |

```text
Create {{ $json.output.image_prompt }} in context of {{ $json.output.post_body }}
with less text content in it but should be understandable to user in 4K resolution.
In the generated image there should be a watermark at the right bottom "Author : Vineet Verma"
```

> **Tip:** Change the watermark name to your own name.

After it runs, the **Output** shows a **binary** file named **`data`**. Click **View** to see the picture.

### Step 10 — Join the text and the picture with Merge

**The problem:** The "Generate an image" node gives out the **picture**, but the post **text** is no longer in its output. The LinkedIn node needs **both**.

**The fix:** Use a **Merge** node to join them, like putting two halves of a sandwich together.

1. Add a **Merge** node.
2. Connect **Generate an image** -> Merge **Input 1**.
3. Also connect **Content creator ( LinkedIn Post )** -> Merge **Input 2**.
   (Drag a second line from the Content creator's output dot to the Merge node's lower input.)
4. Fill in:

| Field | Value |
|---|---|
| Mode | **Combine** |
| Combine By | **Position** |

**Combine by Position** means: join item 1 from Input 1 with item 1 from Input 2.
Result: one item that has **both** the text (`json.output...`) and the picture (`binary.data`).

### Step 11 — Post on LinkedIn

1. Click **+** after Merge, search **LinkedIn**, and choose **Create a post**.
2. Fill in:

| Field | Value |
|---|---|
| Credential | Your LinkedIn credential |
| Post As | **Person** |
| Person Name or ID | Pick your own name from the list |
| Text (Expression) | See below |
| Media Category | **Image** |
| Binary Property | `data` (the name of the picture from Step 9) |
| Additional Fields -> Title | `{{ $json.output.post_title }}` |
| Additional Fields -> Visibility | **Public** |

**Text:**

```text
{{ $json.output.post_title }}

{{ $json.output.post_body }}

{{ $json.output.hashtags }}
```

> **Careful:** Every test run of this node creates a **real** LinkedIn post!
> While testing, **disable** the LinkedIn node (select it and press **D**). Check that the Merge output looks right. Turn it back on only when you are happy.

### Step 12 — Add sticky notes (make it tidy)

1. Right-click on the canvas and choose **Add sticky note** (or use **Shift + S**).
2. Type `## Trigger` in it and drag it behind the Schedule Trigger.
3. Add `## Actions` behind the AI nodes, and `## Results` behind the LinkedIn node.
4. Change colours using the palette icon on the note.

### Step 13 — Test the whole workflow

1. Click **Execute workflow**.
2. Watch each node. A **green tick** means it worked. **Red** means an error.
3. Click any node to see its input and output.

### Step 14 — Save and turn it ON

1. Press **Ctrl/Cmd + S**.
2. Click **Active** (older versions) or **Publish** (newer versions).
3. Done! It will now run by itself every 3 days at 10 AM.
4. Later, open the **Executions** tab to see each automatic run.

### 11.5 How the data changes at each step

| After this node | The data looks like |
|---|---|
| Schedule Trigger | Time details: timestamp, readable date, day of week, and so on. |
| Content Topic Generator | `output: { topic, content_pillar, angle, target_reader, engineering_problem, key_takeaway, hook_direction, suggested_platform }` |
| Content creator ( LinkedIn Post ) | `output: { post_title, post_body, hashtags, image_prompt }` |
| Generate an image | A picture in `binary.data` (plus a little info). |
| Merge | `output: { post_title, post_body, hashtags, image_prompt }` **plus** the picture in `binary.data`. |
| Create a post | LinkedIn's reply, such as the ID of the new post. |

### 11.6 Ideas to make it even better

| Idea | Why | How |
|---|---|---|
| **Human approval before posting** | AI can make mistakes. A human should check before it goes public. | Before the LinkedIn node, add a Gmail, Slack or Telegram node with the **Send and Wait for Response** action. Post only if you approve. |
| **Stop repeated topics** | The system message says "if previously generated topics are supplied...", but right now **nothing supplies them**. So the AI may repeat a topic. | Save each topic in Google Sheets (or an n8n Data Table, if your version has it). Read the old topics before the first agent, and add them to its prompt. |
| **Get told when it fails** | You will not notice a failure if nobody is watching. | Make an **Error Trigger** workflow that emails you, and choose it in this workflow's **Settings -> Error Workflow**. |
| **Save money while testing** | Every AI call costs money. | **Pin** the output of the AI nodes (see [Section 14.3](#143-pin-data-freeze-results-while-testing)). |

---

## 12. Understanding the Workflow JSON File (Every Attribute)

When you export a workflow, n8n saves it as a **JSON file**. This file is the **blueprint** of your workflow. Anyone can import it and get the same boxes and lines.

### 12.1 The skeleton

```json
{
  "name": "04_SocialMediaPostGenerator",
  "nodes": [ ... ],
  "pinData": {},
  "connections": { ... },
  "active": true,
  "settings": { ... },
  "versionId": "528a9902-...",
  "meta": { ... },
  "nodeGroups": [],
  "id": "WsfqHNrQPGIbTeTv",
  "tags": []
}
```

### 12.2 Top-level attributes

| Attribute | Value in our file | What it means |
|---|---|---|
| `name` | `"04_SocialMediaPostGenerator"` | The workflow's name, shown at the top of the editor. |
| `nodes` | A list of 13 nodes | Every box on the canvas, with all its settings. |
| `pinData` | `{}` | Saved "frozen" test data for nodes. Empty means nothing is pinned. |
| `connections` | `{ ... }` | The **address book**: which node sends data to which node. |
| `active` | `true` | The workflow was switched ON when it was exported. |
| `settings` | `{ "executionOrder": "v1", "binaryMode": "separate" }` | Workflow-wide settings (see [12.6](#126-settings)). |
| `versionId` | `"528a9902-..."` | A stamp that changes every time you save. n8n uses it to notice if two people edited at the same time. |
| `meta.instanceId` | `"1e4250e3..."` | A fingerprint of the n8n installation that made this file. Not a password. |
| `meta.templateCredsSetupCompleted` | `true` | The "set up your credentials" helper has been completed. |
| `nodeGroups` | `[]` | A place for groups of nodes. Empty here; you can ignore it. |
| `id` | `"WsfqHNrQPGIbTeTv"` | The workflow's ID inside the n8n where it was made. |
| `tags` | `[]` | Labels for the workflow. Empty here. |

### 12.3 Attributes every node has

Here is one node from our file:

```json
{
  "parameters": {
    "rule": {
      "interval": [
        { "daysInterval": 3, "triggerAtHour": 10 }
      ]
    }
  },
  "type": "n8n-nodes-base.scheduleTrigger",
  "typeVersion": 1.4,
  "position": [-688, 16],
  "id": "b02acf04-c9d7-46db-b358-3488efde6410",
  "name": "Schedule Trigger"
}
```

| Attribute | What it means |
|---|---|
| `parameters` | The fields you filled in inside the node. Different for every node type. |
| `type` | Which kind of node this is. `n8n-nodes-base.something` = a normal built-in node. `@n8n/n8n-nodes-langchain.something` = an AI node. Community nodes have their own names. |
| `typeVersion` | The version of this node's design. When n8n improves a node, old workflows keep their old version so they do not break. Like app versions on your phone. |
| `position` | Where the node sits on the canvas: `[x, y]`. Bigger **x** = further **right**. Bigger **y** = further **down** (the opposite of maths class!). Negative numbers are fine. |
| `id` | A unique random ID for the node, like a roll number. |
| `name` | The name shown on the canvas. **Must be unique** in the workflow. Connections use this name. |
| `credentials` | Which saved credential this node uses (only its ID and name, never the secret). |
| `webhookId` | (Only on trigger nodes that use a web link, like Chat Trigger and Webhook.) The ID used to build the node's web address. |

**Extra attributes you may see in other files** (they appear when you change a node's **Settings** tab):

| Attribute | Meaning |
|---|---|
| `disabled: true` | The node is switched off (you pressed **D**). |
| `notes`, `notesInFlow` | Your note for the node, and whether to show it on the canvas. |
| `retryOnFail`, `maxTries`, `waitBetweenTries` | Try again if it fails, how many times, and how long to wait. |
| `alwaysOutputData` | Pass on an empty item even if there is no result. |
| `executeOnce` | Run only for the first item. |
| `onError` | What to do on error (stop, continue, or use the error output). |

> **Important rule:** n8n only saves settings that you **changed**. If a field still has its default value, it is **not written** in the JSON. That is why some fields you see on screen are missing from the file.

### 12.4 Every node in our file, explained

#### a) Sticky Notes

```json
"parameters": {
  "content": "## Results\n",
  "height": 544,
  "width": 272,
  "color": "#BDB9F9"
}
```

| Parameter | Meaning |
|---|---|
| `content` | The text in the note. It uses Markdown, so `## Results` shows as a heading. `\n` means "new line". |
| `height`, `width` | The size of the note in pixels. |
| `color` | A preset colour number (like `5`) or your own colour code (like `"#BDB9F9"`). Missing = default yellow. |

#### b) Schedule Trigger

```json
"parameters": {
  "rule": {
    "interval": [
      { "daysInterval": 3, "triggerAtHour": 10 }
    ]
  }
}
```

| Parameter | Meaning |
|---|---|
| `rule.interval` | A **list** of timing rules. You can add more than one (for example, also every Monday at 9 AM). |
| `daysInterval: 3` | Run every 3 days. |
| `triggerAtHour: 10` | Run at 10 o'clock (in the workflow's time zone). |
| (missing) `field` | The unit is "days", which is the default, so it is not saved. |
| (missing) `triggerAtMinute` | Minute 0 is the default, so it is not saved. |

#### c) AI Agent — "Content Topic Generator"

```json
"parameters": {
  "promptType": "define",
  "text": "=Generate ONE fresh, specific content topic ... {{ $now }}",
  "hasOutputParser": true,
  "options": {
    "systemMessage": "You are a senior content strategist ..."
  }
},
"type": "@n8n/n8n-nodes-langchain.agent",
"typeVersion": 3.1
```

| Parameter | Meaning |
|---|---|
| `promptType: "define"` | "Source for Prompt" = **Define below** (we type the prompt). The other choice, `"auto"`, takes the message from a Chat Trigger. |
| `text` | The user message (prompt). |
| `=` at the start of `text` | **The value is an Expression.** Any parameter that starts with `=` contains `{{ }}` formulas. |
| `hasOutputParser: true` | "Require Specific Output Format" is ON, so an Output Parser can plug in. |
| `options.systemMessage` | The rules for the AI (system message). |

#### d) Structured Output Parser

```json
"parameters": {
  "schemaType": "manual",
  "inputSchema": "{ \"type\": \"object\", \"properties\": { ... } }"
}
```

| Parameter | Meaning |
|---|---|
| `schemaType: "manual"` | **Define using JSON Schema**. The other choice, `"fromJson"`, means **Generate From JSON Example**. |
| `inputSchema` | The schema, saved as one long text. The `\"` you see are just double quotes written inside text, and `\n` means new line. |

#### e) OpenAI Chat Model

```json
"parameters": {
  "model": {
    "__rl": true,
    "value": "gpt-5-mini",
    "mode": "list",
    "cachedResultName": "gpt-5-mini"
  },
  "builtInTools": {},
  "options": {}
},
"credentials": {
  "openAiApi": { "id": null, "name": "", "__aiGatewayManaged": true }
}
```

| Parameter | Meaning |
|---|---|
| `model` | Which AI model to use. |
| `__rl: true` | This field is a **Resource Locator**: a field where you can pick a value **From list**, **By ID** or **By URL**. |
| `value` | The model you picked: `gpt-5-mini`. |
| `mode: "list"` | You picked it from the drop-down list. |
| `cachedResultName` / `cachedResultUrl` | The name (and link) shown in the box, saved so n8n does not need to look it up again. |
| `builtInTools: {}` | OpenAI's own extra tools (like web search). None are switched on. |
| `options: {}` | Extra options (like temperature or max tokens). None changed. |
| `credentials.openAiApi.id: null` and `__aiGatewayManaged: true` | No personal OpenAI key was saved. The OpenAI access was managed by n8n itself (for example, the free AI credits n8n Cloud gives). On another n8n, you must choose your own OpenAI credential. |

#### f) AI Agent — "Content creator ( LinkedIn Post )"

Same attributes as the first agent:
- `promptType: "define"`
- `text` starts with `=` because it uses `{{ $json.output.topic }}`, `{{ $json.output.angle }}` and `{{ $json.output.target_reader }}`.
- `hasOutputParser: true`
- `options.systemMessage`: a short rule to return only the schema fields.

#### g) Generate an image (OpenAI node)

```json
"parameters": {
  "resource": "image",
  "modelId": { "__rl": true, "value": "gpt-image-2", "mode": "list", "cachedResultName": "GPT-IMAGE-2" },
  "prompt": "=Create  {{ $json.output.image_prompt }} in context of {{ $json.output.post_body }} ...",
  "options": {}
},
"type": "@n8n/n8n-nodes-langchain.openAi",
"typeVersion": 2.3
```

| Parameter | Meaning |
|---|---|
| `resource: "image"` | We are working with images (other choices: text, audio, file...). |
| (missing) `operation` | "Generate an Image" is the default, so it is not saved. |
| `modelId` | The image model, as a Resource Locator: `gpt-image-2`. |
| `prompt` | What to draw (an Expression, so it starts with `=`). |
| `options` | Extra settings like size or quality. None changed. |

#### h) Merge

```json
"parameters": {
  "mode": "combine",
  "combineBy": "combineByPosition",
  "options": {}
}
```

| Parameter | Meaning |
|---|---|
| `mode: "combine"` | Join the two inputs into single items (instead of just putting them one after another, which is `append`). |
| `combineBy: "combineByPosition"` | Join item 1 with item 1, item 2 with item 2, and so on. Other choices: by matching fields, or all possible combinations. |

#### i) Create a post (LinkedIn)

```json
"parameters": {
  "person": "HzZB5llAwV",
  "text": "={{ $json.output.post_title }}\n\n{{ $json.output.post_body }}\n\n{{ $json.output.hashtags }}\n\n",
  "shareMediaCategory": "IMAGE",
  "additionalFields": {
    "title": "={{ $json.output.post_title }}",
    "visibility": "PUBLIC"
  }
},
"credentials": {
  "linkedInOAuth2Api": { "id": "cKimm2L5yzFgtIch", "name": "LinkedIn account" }
}
```

| Parameter | Meaning |
|---|---|
| (missing) `postAs` | "Person" is the default, so it is not saved. |
| `person` | The LinkedIn ID of the person who posts. **You must change this to your own** after importing. |
| `text` | The post text: title, body and hashtags with empty lines between them. |
| `shareMediaCategory: "IMAGE"` | The post includes an image (from `binary.data`). |
| `additionalFields.title` | The title for the shared image. |
| `additionalFields.visibility: "PUBLIC"` | Everyone can see the post. The other choice is connections only. |
| `credentials.linkedInOAuth2Api` | Points to a LinkedIn credential called "LinkedIn account" by its ID. On another n8n this ID does not exist, so you pick your own. |

### 12.5 Connections — the address book

The `connections` part says **who sends data to whom**. Let us read one entry:

```json
"Content creator ( LinkedIn Post )": {
  "main": [
    [
      { "node": "Generate an image", "type": "main", "index": 0 },
      { "node": "Merge",             "type": "main", "index": 1 }
    ]
  ]
}
```

**Read it aloud:** "From the node **Content creator ( LinkedIn Post )**, using its normal (**main**) output number **0**, send the data to **two** places: **Generate an image** (into its input 0) and **Merge** (into its input 1, which is Input 2 on screen)."

**What each bracket means:**

```text
"Source node name": {               <- the node that SENDS data
  "main": [                         <- the kind of line (main / ai_languageModel / ai_tool ...)
    [                               <- output number 0 of the source node
      { "node": "Target", "type": "main", "index": 0 }   <- one receiver
    ],
    [ ... ]                         <- output number 1 (only for nodes like If)
  ]
}
```

| Part | Meaning |
|---|---|
| Outer key (`"Content creator ( LinkedIn Post )"`) | The **sending** node, found by its **name**. |
| `"main"` / `"ai_languageModel"` / ... | The **kind** of connection. |
| Outer `[ ]` | A list of the sending node's **outputs**. 1st `[ ]` = output 0, 2nd `[ ]` = output 1, ... |
| Inner `[ ]` | All the nodes connected to that one output. |
| `"node"` | The **receiving** node's name. |
| `"type"` | The kind of input on the receiving node. |
| `"index"` | **Which input** of the receiving node. `0` = first input, `1` = second input. |

**Example with an If node** (two outputs):

```json
"If": {
  "main": [
    [ { "node": "Send Email",   "type": "main", "index": 0 } ],
    [ { "node": "Do Nothing",   "type": "main", "index": 0 } ]
  ]
}
```

The first list is the **true** path. The second list is the **false** path.

**All connections in our file:**

| From (sender) | Kind | To (receiver) | Input index |
|---|---|---|---|
| Schedule Trigger | `main` | Content Topic Generator | 0 |
| OpenAI Chat Model | `ai_languageModel` | Content Topic Generator | 0 |
| Structured Output Parser | `ai_outputParser` | Content Topic Generator | 0 |
| Content Topic Generator | `main` | Content creator ( LinkedIn Post ) | 0 |
| OpenAI Chat Model1 | `ai_languageModel` | Content creator ( LinkedIn Post ) | 0 |
| Structured Output Parser1 | `ai_outputParser` | Content creator ( LinkedIn Post ) | 0 |
| Content creator ( LinkedIn Post ) | `main` | Generate an image | 0 |
| Content creator ( LinkedIn Post ) | `main` | Merge | **1** (Input 2) |
| Generate an image | `main` | Merge | **0** (Input 1) |
| Merge | `main` | Create a post | 0 |

> **Notice:** For AI connections, the **helper node is the sender**. The chat model "plugs into" the agent, so the JSON says "OpenAI Chat Model -> Content Topic Generator".

> **Careful:** Connections use node **names**. If you rename a node by editing the JSON by hand, you must also change its name everywhere in `connections`. Renaming inside the n8n editor does this for you.

### 12.6 Settings

| Setting | Value in our file | Meaning |
|---|---|---|
| `executionOrder` | `"v1"` | The order in which branches run. **v1** (recommended) finishes one branch fully before starting the next, going from the top branch to the bottom branch on the canvas. The old **v0** ran the first node of every branch, then the second node of every branch, and so on. |
| `binaryMode` | `"separate"` | How files (binary data) are kept with items. `separate` keeps files in their own `binary` part, apart from the normal JSON. Leave it as it is. |

**Other settings you may see** (change them from the **...** menu -> **Settings**):

| Setting | Meaning |
|---|---|
| `timezone` | The time zone for this workflow (very important for Schedule Triggers). |
| `errorWorkflow` | Which workflow to run if this one fails. |
| `saveDataSuccessExecution` | Keep or throw away the data of successful runs. |
| `saveDataErrorExecution` | Keep or throw away the data of failed runs. |
| `saveManualExecutions` | Keep the data of test runs you start by hand. |
| `saveExecutionProgress` | Save after each node, so a crashed run can be checked. |
| `executionTimeout` | Stop the workflow if it runs longer than this many seconds. |
| `callerPolicy` | Which other workflows are allowed to call this one. |

### 12.7 The other workflows in this folder

| File | Trigger | Main nodes | What it does |
|---|---|---|---|
| [`01_JiraTicket Fetching.json`](./01_JiraTicket%20Fetching.json) | Chat Trigger | AI Agent, OpenAI Chat Model, Simple Memory, Jira Tool | You ask for a Jira ticket in chat; the agent finds the issue key and fetches the ticket. |
| [`02_Create JiraTicket.json`](./02_Create%20JiraTicket.json) | Chat Trigger | AI Agent, OpenAI Chat Model, Simple Memory, Jira Tool | You describe a subtask; the agent fills the fields and creates a Jira subtask. |
| [`03_FetchJiraAndCreateTestCase.json`](./03_FetchJiraAndCreateTestCase.json) | Chat Trigger | AI Agent, Groq Chat Model, Simple Memory, Jira Tool (plus an unused Ollama Chat Model) | Fetches a Jira issue so the agent can create test cases from it. |
| [`04_SocialMediaPostGenerator.json`](./04_SocialMediaPostGenerator.json) | Schedule Trigger | 2 AI Agents, 2 OpenAI Chat Models, 2 Structured Output Parsers, OpenAI image, Merge, LinkedIn | The example in this chapter. |

**Two things to learn from file 03:**

1. **`$fromAI()`** — In the Jira Tool, the Issue Key is:
   ```text
   ={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('Issue_Key', ``, 'string') }}
   ```
   This means: "Let the AI fill this field." If you type "show me KAN-1" in chat, the agent puts `KAN-1` here by itself. You turn this on by clicking the small **AI sparkle button** next to a field in a tool node.

2. **An empty connection** — The file has:
   ```json
   "Ollama Chat Model": { "ai_languageModel": [ [] ] }
   ```
   The empty `[ ]` means the Ollama node **was** connected once, but now it is connected to **nothing**. It is a leftover. Only the Groq model is really being used.

---

## 13. Export and Import

### 13.1 Why export and import?

- **Backup:** keep a copy in case something breaks.
- **Share:** give your workflow to a friend or team.
- **Move:** take a workflow from local n8n to Cloud, or the other way.
- **Version control:** save it in Git (like this repository does!) and see changes over time.

### 13.2 How to export

**Way 1: Download from the editor (easiest)**
1. Open the workflow.
2. Click the **...** (three dots) menu at the top right.
3. Click **Download**.
4. A `.json` file is saved to your Downloads folder.

**Way 2: Copy and paste**
1. Click on the canvas and press **Ctrl/Cmd + A** (select all).
2. Press **Ctrl/Cmd + C** (copy).
3. Paste into any text editor. You now have the JSON.
   (You can also copy just a few selected nodes.)

**Way 3: Command line (local n8n)**

```bash
# Export one workflow by its ID
n8n export:workflow --id=WsfqHNrQPGIbTeTv --output=04_SocialMediaPostGenerator.json

# Export ALL workflows, one file each, into a folder
n8n export:workflow --all --separate --output=backups/

# Export credentials (still locked/encrypted)
n8n export:credentials --all --output=credentials.json
```

**Way 4: Command line inside Docker**

```bash
docker exec -it n8n n8n export:workflow --all --separate --output=/home/node/.n8n/backups/
docker cp n8n:/home/node/.n8n/backups ./backups
```

> **Careful:** `n8n export:credentials` also has a `--decrypted` option that saves your secrets as **plain text**. Avoid it. If you must use it, never share or commit that file.

### 13.3 How to import

**Way 1: Import from a file (easiest)**
1. Click **Create Workflow** to open an empty workflow.
2. Click the **...** menu -> **Import from File...**
3. Choose the `.json` file (for example `04_SocialMediaPostGenerator.json`).
4. The nodes appear on the canvas. Click **Save**.

**Way 2: Import from a URL**
- **...** menu -> **Import from URL...** -> paste a link to a raw JSON file (for example a raw GitHub link).

**Way 3: Paste**
- Copy the JSON text, click on an empty canvas, and press **Ctrl/Cmd + V**.

**Way 4: Command line (local n8n)**

```bash
# Import one file
n8n import:workflow --input=04_SocialMediaPostGenerator.json

# Import a folder of files
n8n import:workflow --separate --input=backups/
```

**Way 5: Templates**
- Go to **https://n8n.io/workflows**, find a template you like, and click **Use workflow**. It copies it into your n8n.

### 13.4 After importing — the checklist

An imported workflow will not work straight away. Go through this list for `04_SocialMediaPostGenerator.json`:

- [ ] **Credentials:** Open each node that shows a warning. Pick your own **OpenAI** credential (3 nodes) and **LinkedIn** credential (1 node).
- [ ] **LinkedIn person:** In "Create a post", choose **your** name in **Person**. (The file has someone else's ID, `HzZB5llAwV`.)
- [ ] **Models:** Check that `gpt-5-mini` and `gpt-image-2` are available to your account. Pick another model if not.
- [ ] **Watermark:** Change "Author : Vineet Verma" in the image prompt to your name.
- [ ] **Time zone:** Check **...** -> **Settings** -> **Timezone**.
- [ ] **Test safely:** Disable the LinkedIn node (**D**), click **Execute workflow**, check each output.
- [ ] **Turn it on:** Enable the LinkedIn node, save, and click **Active / Publish**.

> An imported workflow usually comes in **switched OFF**, even if the file says `"active": true`. This is a safety feature, so it does not start running before you fix the credentials.

### 13.5 What is inside an exported file?

| Thing | Included? |
|---|---|
| Nodes and their settings | Yes |
| Connections (lines) | Yes |
| Workflow settings | Yes |
| Sticky notes | Yes |
| Pinned test data | Yes (if any) |
| Tags | Yes |
| Credential **name and ID** | Yes |
| Credential **secrets** (API keys, passwords) | **No** |
| Past runs (execution history) | **No** |

### 13.6 Moving all your work to a new n8n

1. Export all workflows (`n8n export:workflow --all --separate --output=backups/`).
2. Export credentials (`n8n export:credentials --all --output=credentials.json`).
3. On the new n8n, import both with `n8n import:workflow` and `n8n import:credentials`.
4. **Important:** Credentials are locked with the old n8n's **encryption key**. The new n8n must use the **same** `N8N_ENCRYPTION_KEY`, or the credentials cannot be opened. Otherwise, just create the credentials again by hand.

### 13.7 Safety check before you share a JSON file

Secrets in **credentials** are safe. But secrets can sneak into other places. Check these:

| Where to look | What could leak |
|---|---|
| `pinData` | Real data from a test run (emails, names, ticket text). |
| HTTP Request node headers or URL | An API key typed straight into the field. |
| Code node | Passwords or keys written in the code. |
| Personal IDs | Like the LinkedIn `person` ID, Jira site address, project keys. |
| Prompts | Private company information. |

> **Rule:** Never type a secret directly into a node. Always use a **credential**.

---

## 14. Running, Testing and Fixing Workflows

### 14.1 Test runs vs real runs

| Type | How it starts | Where you see it |
|---|---|---|
| **Manual (test) execution** | You click **Execute workflow** or **Execute step**. | Right on the canvas and in the Logs panel. |
| **Production execution** | The trigger fires by itself, because the workflow is **Active / Published**. | In the **Executions** list. |

### 14.2 The Executions list

Open the **Executions** tab of a workflow (or Overview -> **Executions** for all workflows).

| Status | Meaning |
|---|---|
| **Success** | Everything worked. |
| **Error** | Something failed. Click it to see which node and why. |
| **Running** | It is running right now. |
| **Waiting** | It is paused (for example at a Wait node, or waiting for your approval). |

Click any run to see exactly what each node received and sent. You can also copy a failed run back into the editor (**Debug in editor** / **Copy to editor**, depending on your plan) to fix it with the same data.

### 14.3 Pin data (freeze results while testing)

Every AI call costs money and time. **Pinning** saves a node's output, so the next test uses the saved result instead of calling the AI again.

1. Run the node once.
2. In the **Output** panel, click the **pin** icon (or select the node and press **P**).
3. The node turns purple-ish and shows a pin. It will not really run until you unpin it.

> **Careful:** Pinned data is used **only in test runs**. Unpin before you finish, so you do not get confused later.

### 14.4 Other testing tricks

- **Execute step:** run only up to one node.
- **Disable a node (D):** skip a node, for example the LinkedIn node, while testing.
- **Manual Trigger:** add one next to the Schedule Trigger when you want an easy "Run now" button.
- **Edit output:** in the Output panel you can edit pinned data to test special cases.

### 14.5 Common problems and fixes

| Problem | Likely reason | Fix |
|---|---|---|
| Red warning "Credentials not set" | The workflow was imported, so credentials are missing. | Open the node and pick your own credential. |
| `$json.output.topic` shows as empty / undefined | The previous node did not give an `output` field (for example, the Output Parser is not connected). | Turn ON **Require Specific Output Format** and connect the Output Parser. Check the field names in the Input panel. |
| "Could not parse the output" | The AI did not follow the schema. | Make the system message clearer, use a stronger model, or turn on the parser's auto-fix option if your version has it. |
| LinkedIn post has no picture | The picture was lost, or the binary name is not `data`. | Make sure the Merge node joins the image (Input 1) and the text (Input 2). Check **Binary Property** = `data`. |
| Workflow never runs by itself | It is not **Active / Published**, or local n8n was off. | Turn it on. Keep n8n running or use Cloud. |
| Runs at the wrong time | Wrong time zone. | Set the time zone in workflow Settings or with `GENERIC_TIMEZONE`. |
| Webhook works in test but not for real | You used the **Test URL**. | Use the **Production URL** and make sure the workflow is active. |
| "429 Too Many Requests" / quota error | Too many API calls, or no money left on the AI account. | Wait, add **Retry On Fail**, or add billing to the AI account. |
| Same topic again and again | Nothing tells the AI about older topics. | Store old topics and add them to the prompt (see [11.6](#116-ideas-to-make-it-even-better)). |
| Docker n8n cannot reach Ollama | `localhost` inside Docker is the container. | Use `http://host.docker.internal:11434`. |

### 14.6 Get alerts when something fails (Error Workflow)

1. Create a new workflow with an **Error Trigger** node.
2. After it, add a Gmail / Slack / Telegram node that sends you a message like:
   `Workflow {{ $json.workflow.name }} failed: {{ $json.execution.error.message }}`
3. Save it.
4. In your main workflow: **...** -> **Settings** -> **Error Workflow** -> choose the new one.

Now, whenever the main workflow fails, you get a message.

---

## 15. Good Habits

1. **Name every node clearly.** "Content Topic Generator" is better than "AI Agent2".
2. **Use sticky notes** to explain groups of nodes.
3. **One job per workflow.** Split big jobs into **sub-workflows** with the **Execute Workflow** node.
4. **Test with a Manual Trigger** before switching the workflow on.
5. **Pin data** while testing to save money and time.
6. **Never type secrets into nodes.** Always use credentials.
7. **Keep a human in the loop** for anything public or risky (posting, emailing customers, creating Jira tickets).
8. **Use Structured Output Parsers** so AI answers always have the same shape.
9. **Set an Error Workflow** so you know when something breaks.
10. **Set the time zone** for anything with a Schedule Trigger.
11. **Export and save your workflows in Git** (like this folder) so you have a backup and a history.
12. **Number your files** (01_, 02_, 03_...) so they stay in order.
13. **Watch your AI costs.** Every AI call costs money. Do not schedule AI workflows more often than you need.
14. **Check the AI's work.** AI can be wrong. Never trust its output blindly.

---

## 16. Handy Keyboard Shortcuts

On Mac use **Cmd**. On Windows/Linux use **Ctrl**. Shortcuts can change a little between versions; hover over a button to see its shortcut.

| Shortcut | What it does |
|---|---|
| **Tab** | Open the nodes panel. |
| **Ctrl/Cmd + S** | Save. |
| **Ctrl/Cmd + Enter** | Execute the workflow. |
| **Ctrl/Cmd + Z** | Undo. |
| **Ctrl/Cmd + A** | Select all nodes. |
| **Ctrl/Cmd + C / V** | Copy / paste nodes (as JSON). |
| **Delete / Backspace** | Delete the selected node. |
| **F2** | Rename the selected node. |
| **D** | Disable / enable the selected node. |
| **P** | Pin / unpin the selected node's data. |
| **Shift + S** | Add a sticky note. |
| **1** | Zoom to fit everything. |
| **0** | Reset zoom. |
| **+ / -** | Zoom in / out. |

---

## 17. Glossary

| Word | Meaning |
|---|---|
| **Action** | Something a node does, like "Create a post". |
| **Active / Published** | The workflow is ON and runs by itself. |
| **AI Agent** | An AI node that can think, use tools and memory to finish a task. |
| **API** | A way for two programs to talk to each other. |
| **API key** | A secret password that lets a program use an API. |
| **Binary data** | Files such as images, PDFs and audio. |
| **Branch** | One path in a workflow when the lines split. |
| **Canvas** | The board where you place nodes. |
| **Chat Model** | The AI "brain" plugged into an AI Agent. |
| **Cloud** | n8n running on n8n's own servers on the internet. |
| **Connection** | A line between nodes that carries data. |
| **Container** | A sealed box (from Docker) holding an app and everything it needs. |
| **Credential** | Saved login details for an app. |
| **Docker** | A tool that runs apps inside containers. |
| **Encryption key** | The secret key n8n uses to lock your credentials. |
| **Environment variable** | A setting given to n8n when it starts, like `GENERIC_TIMEZONE`. |
| **Execution** | One run of a workflow. |
| **Export** | Save a workflow as a JSON file. |
| **Expression** | A formula inside `{{ }}` that uses data from earlier nodes. |
| **Import** | Load a workflow from a JSON file. |
| **Item** | One piece of data moving between nodes. |
| **JSON** | A text format for data using `{ }`, `[ ]` and `"name": value`. |
| **JSON Schema** | A description of what shape some JSON must have. |
| **LLM** | Large Language Model, the type of AI that writes text (like GPT). |
| **localhost** | "This computer." |
| **Memory** | A helper node that lets an AI Agent remember past messages. |
| **Node** | One box (one step) in a workflow. |
| **OAuth2** | A safe login method with a "Sign in with..." pop-up. |
| **Output Parser** | A helper node that forces the AI's answer into fixed fields. |
| **Pin data** | Save a node's output so tests reuse it. |
| **Port** | A "door number" on a computer, like 5678 for n8n. |
| **Production URL** | The real webhook link that works when the workflow is active. |
| **Prompt** | The message or question you give the AI. |
| **Resource Locator** | A field where you choose something from a list, by ID, or by URL (`__rl` in JSON). |
| **Schedule Trigger** | A trigger that starts a workflow at set times. |
| **Self-hosted** | Running n8n on your own computer or server. |
| **Sticky Note** | A coloured note on the canvas. Does not run. |
| **Sub-node** | A helper node that plugs into an AI root node (model, memory, tool, parser). |
| **Sub-workflow** | A workflow called by another workflow. |
| **System message** | The rules the AI must follow. |
| **Template** | A ready-made workflow you can copy. |
| **Test URL** | The webhook link that works only while testing. |
| **Tool** | Something an AI Agent can use, like the Jira Tool. |
| **Trigger** | The node that starts a workflow. |
| **typeVersion** | The version of a node's design. |
| **Webhook** | A web link that starts a workflow when something calls it. |
| **Workflow** | A full automatic job made of nodes and connections. |

---

## 18. Practice Time

Try these in order. Each one is a little harder.

**Exercise 1 — Hello, n8n!**
1. Create a new workflow.
2. Add a **Manual Trigger**.
3. Add an **Edit Fields (Set)** node. Add a field `message` with the value `Hello {{ $now.toFormat('dd-MM-yyyy') }}`.
4. Click **Execute workflow** and look at the output.

**Exercise 2 — A joke every morning**
1. Use a **Schedule Trigger**: every day at 8 AM.
2. Add an **HTTP Request** node: Method `GET`, URL `https://official-joke-api.appspot.com/random_joke`.
3. Add an **Edit Fields** node that makes one field: `{{ $json.setup }} ... {{ $json.punchline }}`.
4. Test it with **Execute workflow**.

**Exercise 3 — Even or odd?**
1. Manual Trigger -> Edit Fields with a number field `n` = `7`.
2. Add an **If** node: condition `{{ $json.n % 2 }}` is equal to `0`.
3. On the **true** path, add Edit Fields `result = even`. On the **false** path, `result = odd`.
4. Change `n` and test again.

**Exercise 4 — Import our example safely**
1. Import [`04_SocialMediaPostGenerator.json`](./04_SocialMediaPostGenerator.json).
2. Connect your own OpenAI credential.
3. **Replace** the LinkedIn node with a **Gmail -> Send a message** node that emails the post (and the picture as an attachment) to **yourself**.
4. Run it and read the post in your inbox.

**Exercise 5 — Add a human approval step**
1. In the workflow from Exercise 4, add a Gmail (or Slack / Telegram) node with **Send and Wait for Response** before the final step.
2. Only continue if you click **Approve**.
3. Think: why is this safer for something that posts in public?

**Exercise 6 — Export and read the JSON**
1. Download your Exercise 3 workflow.
2. Open the file in VS Code.
3. Find the `If` node in `connections`. Which list is the **true** path and which is the **false** path?

---

## 19. Quick Quiz

1. What is a **node**?
2. Which kind of node starts a workflow?
3. On local n8n, which address do you open in your browser?
4. What does `{{ $json.output.topic }}` mean?
5. Why does our workflow need a **Merge** node?
6. What is the difference between a **system message** and a **user message**?
7. Are your API keys saved inside an exported workflow JSON file?
8. Why might a Schedule Trigger not run on local n8n?
9. In the JSON `connections`, what does `"index": 1` on the Merge node mean?
10. What does an `=` at the start of a parameter value in the JSON mean?
11. What is the difference between an **AI Agent** and a **Basic LLM Chain**?
12. What is **pinned data** used for?
13. Why do some fields you see on screen not appear in the JSON file?
14. What does `$fromAI()` do?

<details>
<summary><b>Click to see the answers</b></summary>

1. One box in a workflow. It does one step of the job.
2. A **trigger** node (for example Schedule Trigger, Webhook, Chat Trigger, Manual Trigger).
3. `http://localhost:5678`
4. "Take the `topic` field from inside `output`, from the item that came into this node."
5. The image node outputs only the picture. The LinkedIn node needs both the picture and the text. Merge joins them into one item.
6. The system message gives the **rules** (who the AI is and what it must or must not do). The user message is the **actual task** for this run.
7. **No.** Only the credential's name and ID are saved. (But be careful about secrets typed into nodes or saved in `pinData`.)
8. Because the computer was off or asleep, n8n was not running, or the workflow was not active. A wrong time zone can also make it run at a different time.
9. The data goes into the Merge node's **second** input (shown as **Input 2** on screen). `0` is the first input.
10. The value is an **Expression** (it contains `{{ }}` formulas).
11. An AI Agent can use tools and memory and think in several steps. A Basic LLM Chain just asks one question and gets one answer.
12. To save a node's output so that test runs reuse it, which saves time and AI costs.
13. n8n only saves values you **changed**. Default values are left out to keep the file small.
14. It lets the AI Agent fill a tool's field by itself, for example finding the Jira issue key from your chat message.

</details>

---

## 20. Chapter Summary

- **n8n** is a tool to build automatic jobs (**workflows**) by joining boxes (**nodes**) with lines (**connections**).
- Every workflow starts with a **trigger**. Our example uses a **Schedule Trigger** (every 3 days at 10 AM).
- Data moves as **items** in **JSON**. Files like images move as **binary** data.
- You can run n8n on **Cloud** (easy, always on, paid) or **Local** with `npx n8n` or **Docker** (free, private, must stay running). Local n8n opens at `http://localhost:5678`.
- **Expressions** like `{{ $json.output.topic }}` let one node use data from another.
- **Credentials** keep your keys safe and are **not** included in exported files.
- **AI Agents** need a **Chat Model**. They can also use **Memory**, **Tools** and an **Output Parser**.
- A **Structured Output Parser** makes the AI's answer always have the same fields.
- A **Merge** node joins two paths of data, like text and a picture.
- An exported workflow is a **JSON blueprint** with `nodes`, `connections`, `settings` and a few ID fields.
- **Import** with **...** -> **Import from File**, then reconnect credentials and test before turning it on.
- Test with **Execute step**, **pin data**, and **disable** risky nodes. Check past runs in **Executions**.
- Always keep a **human** checking AI work before it goes public.

### Useful links

| Link | What you find there |
|---|---|
| https://docs.n8n.io | Official n8n documentation. |
| https://n8n.io/workflows | Thousands of ready-made templates. |
| https://community.n8n.io | Forum to ask questions. |
| https://n8n.io/pricing | Cloud plans and prices. |

---

*Next step: open [`04_SocialMediaPostGenerator.json`](./04_SocialMediaPostGenerator.json) next to Section 12 and try to find every attribute in the file yourself.*
