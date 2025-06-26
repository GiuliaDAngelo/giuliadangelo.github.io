# Giulia D'Angelo's Personal Website

This repository contains the source code and content for Dr. Giulia D'Angelo's personal academic and professional website. It is built with the [Hugo](https://gohugo.io/) static site generator.

This guide is intended for Giulia and other contributors to help with running the site locally, making content updates, and getting development help.

## Table of Contents

- [Running the Site Locally](#running-the-site-locally)
   - [Prerequisites](#prerequisites)
   - [Installation & Launch](#installation--launch)
- [How to Update Your Website](#how-to-update-your-website)
   - [Editing Homepage Sections](#editing-homepage-sections)
   - [Adding a New Grant or Award](#adding-a-new-grant-or-award)
   - [Adding New Publications or Experiences](#adding-new-publications-or-experiences)
   - [Adding Images](#adding-images)
- [Automatic Deployment](#automatic-deployment)
- [Getting Help with AI (Advanced)](#getting-help-with-ai-advanced)
- [Key Project Directories](#key-project-directories)

## Running the Site Locally

To make and preview changes on your own computer before they go live, you'll need to set up a local development environment.

### Prerequisites

You will need to install the following software. If you already have them, you can skip to the next section.

1.  **Git:** A version control system used to manage and download the project code.
   *   [Installation instructions for Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

2.  **Hugo (Extended Version):** The core software that builds the website. It's crucial to install the **"extended"** version.
   *   [Installation instructions for Hugo](https://gohugo.io/installation/). Follow the steps for your operating system (macOS, Windows, or Linux).

3.  **Node.js and npm:** A JavaScript runtime and package manager. While not strictly required for basic content edits, it's good practice to have it installed for this project.
   *   [Installation instructions for Node.js (includes npm)](https://nodejs.org/en/download/)

### Installation & Launch

Once the prerequisites are installed, follow these steps in your terminal or command prompt:

1.  **Clone the repository:**
    This downloads a copy of the website's code to your computer.
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
    cd YOUR_REPOSITORY_NAME
    ```

2.  **Start the Hugo server:**
    This command builds the website and starts a local server so you can see it in your browser.
    ```bash
    hugo server
    ```

3.  **View your website:**
    Open your web browser and navigate to `http://localhost:1313`. You should see a live, local version of your website. Any changes you save to the project files will now appear here instantly.

## How to Update Your Website

Most of the website's content is stored in simple text files that are easy to edit. You don't need to write any code.

### Editing Homepage Sections

The content for the main sections on the homepage (Hero, About Me, Expertise) is located in the `data/` directory.

-   **About Me:** Edit the file `data/aboutSection.yml`
-   **Expertise:** Edit the file `data/expertiseSection.yml`
-   **Hero Text:** Edit the file `data/hero.yml`

These are YAML files, which have a simple `key: value` format. You can change the text after the colon. For longer text blocks, you can use `>` to allow for multiple lines.

### Adding a New Grant or Award

The "Grants & Awards" section is managed in `data/grantsSection.yml`. To add a new award:

1.  Open `data/grantsSection.yml`.
2.  Scroll down to the `awards:` list.
3.  Copy an existing award entry (from the `- image:` line to the `url2_text:` line).
4.  Paste it as a new item in the list and update the details (title, image, description, etc.).

Example of a single award entry:
```yaml
- image: "images/awards/new-award-image.png"
  title: "New Prestigious Award 2026"
  category: "Cool Institution"
  description: "A description of why this award is awesome."
  url: "https://example.com/award-details"
  url_text: "See Details"
  ```

### Adding New Publications or Experiences

Your resume, including experience, publications, and education, is managed in `data/resumeSection.yml`.

1.  Open `data/resumeSection.yml`.
2.  Find the relevant list: `experience:`, `publications:`, or `education:`.
3.  Copy an existing entry (from `- content:` to `time:`) and paste it at the top of the list to add a new item.
4.  Update the text and time fields. The content uses Markdown, so you can use `*` for italics or `**` for bold.

### Adding Images

1.  Place your new image file inside the `static/images/` directory. It's helpful to organize them into subfolders (e.g., `static/images/awards/`).
2.  In the `.yml` or `.md` file, reference the image using its path relative to `static/`, for example: `images/awards/new-award-image.png`.

## Automatic Deployment

The website is set up with a GitHub Actions workflow (`.github/workflows/hugo-deploy.yml`). This means that any changes you **push to the `main` branch** of the repository will automatically be built and deployed to the live website. The process usually takes a few minutes.

This allows you to make edits directly in GitHub's web interface if you're away from your computer, but the recommended workflow is to test changes locally first.

## Getting Help with AI (Advanced)

If you want to make bigger changes, add new features, or fix something that's broken, you can get very effective help from an AI assistant. To do this, you need to provide the AI with the full context of the project.

The `generate_context.py` script in this repository is designed for exactly this purpose.

1.  **Prerequisite:** Make sure you have Python 3 installed on your computer.

2.  **Run the script:**
    Open your terminal, navigate to the project's root directory, and run:
    ```bash
    python3 generate_context.py --full
    ```

3.  **What it does:**
    This command reads all the important files in your project and combines them into a single, large text file located at `tmp/output_full.txt`. It intelligently excludes unnecessary files (like libraries and large images) to keep the output focused.

4.  **How to use it:**
    Open `tmp/output_full.txt`, copy its entire contents, and paste it into your chat with an AI assistant. You can then ask your question, for example:
    > "Here is the full context for my website. Can you help me add a new 'Teaching' section to the homepage right after the 'Resume' section?"

The AI will now have all the information it needs to give you precise, accurate instructions and code.

## Key Project Directories

-   `data/`: Contains `.yml` files that hold most of the site's content (About, Resume, Awards, etc.). **This is where you'll make most content edits.**
-   `content/`: Contains Markdown files for individual pages like blog posts.
-   `layouts/`: Contains the HTML templates that structure the website. Editing these files requires knowledge of HTML and Hugo templating.
-   `assets/`: Contains the site's stylesheets (SCSS) and JavaScript files.
-   `static/`: Contains static files like images, fonts, and PDFs. **Place new images in `static/images/`.**