# 📸 AI Agent Media Posting Guide

This guide explains how to provide images to your EasyPost AI Agent so it can automatically post them to your connected social media handles (Facebook Page & Instagram Business).

## 🚀 1. Posting via WhatsApp (WAHA)

The system is configured with "Self-Healing Mirroring." When you send an image to your WhatsApp bot, it automatically mirrors the image to a public S3 bucket so that Meta (Facebook/Instagram) can access it for posting.

### Step-by-Step:
1. **Send the Image**: Send any photo to your WhatsApp bot number.
2. **Add a Caption**: You can send a caption with the image or in the message immediately following it.
3. **Ask to Post**: Type a command like:
   - *"Post this to Instagram with the caption: My new product launch! #vibes"*
   - *"Upload this photo to Facebook and Instagram please."*
4. **Approval (Optional)**: If you have human-in-the-loop enabled, the agent will ask for your confirmation before finalizing the post.

---

## 💬 2. Posting via Chat Section (Web Dashboard)

In the web dashboard, the agent can process images via URLs or uploaded assets.

### Step-by-Step:
1. **Using a URL**: If you have an image hosted online, simply paste the URL and tell the agent what to do:
   - *"Hey, use this image: https://example.com/photo.jpg and post it to my Facebook page."*
2. **Upload (Frontend Integration)**: 
   - When you upload an image in the chat UI, the frontend sends the image to our S3 service first.
   - The resulting **S3 URL** is then sent to the AI Agent in the message background.
   - You can then simply say: *"Post my last upload to all platforms."*

---

## 🛠️ 3. How the Agent Handles Media (Technical)

Your agent uses **MCP (Model Context Protocol)** tools to communicate with social platforms. Here is what happens behind the scenes:

### The `media_id` Parameter
The agent's tools (`post_image_to_instagram`, `post_image_to_facebook`) primarily require a `media_id`.
- **In WhatsApp**: The bot automatically resolves the WhatsApp `media_id` and converts it into a public `s3_url` before calling the tool.
- **In Chat**: The bot assumes the provided URL or ID is accessible and passes it directly to the Meta API.

### Multi-Platform Posting
You can trigger a simultaneous post to all platforms using a single command:
> *"Post this image to all platforms with a professional tone."*

The agent will call the `post_image_to_all_platforms` tool, which handles the complex concurrent execution to both Facebook and Instagram in one handshake.

---

## 💡 Pro-Tips for Better Posts
- **Tone Control**: Mention your preferred tone! *"Post this to Instagram in a quirky/funny tone."*
- **Hashtag Analysis**: Ask the agent to generate hashtags first. *"Analyze this image and suggest 10 trending hashtags before posting."*
- **Scheduling**: You can also ask to schedule text posts (Facebook only for now). *"Schedule a post for 5 PM tomorrow saying 'Weekend is coming!'"*

---

**Note**: Ensure your nodes are "Operational" on the Dashboard before asking the agent to post. If the handshake is broken, the agent will inform you that it cannot reach the platform.
