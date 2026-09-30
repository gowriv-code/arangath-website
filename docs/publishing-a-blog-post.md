# Publishing a blog post

You write posts in a web page at **arangath.co.uk/admin**. No code, no terminal.

## One-time setup (Vish or whoever owns the GitHub account, about 10 minutes)

The editor signs you in with your GitHub account. Netlify passes the sign-in through, so you need to switch that on once.

1. On GitHub, open **Settings > Developer settings > OAuth Apps > New OAuth App**.
   - Application name: Arangath blog editor
   - Homepage URL: https://arangath.co.uk
   - Authorization callback URL: `https://api.netlify.com/auth/done`
2. Click **Register application**. Copy the **Client ID**, then click **Generate a new client secret** and copy the secret.
3. In Netlify, open the site, then **Site configuration > Access & security > OAuth**. Under **Authentication providers**, click **Install provider**, choose **GitHub**, and paste the Client ID and secret.
4. Make sure everyone who will write posts has a GitHub account that has **write access** to the `gowriv-code/arangath-website` repository (repository **Settings > Collaborators**).

Netlify Identity and Git Gateway are deprecated, which is why this uses GitHub sign-in instead.

## Writing and publishing a post

1. Go to **arangath.co.uk/admin** and click **Login with GitHub**.
2. Click **Blog posts**, then **New Blog post**.
3. Fill in the fields:
   - **Title**: what readers see at the top.
   - **URL slug**: lower case, words joined by hyphens, for example `why-clash-reports-fail`.
   - **Date**: the publication date. Newest posts appear first.
   - **Summary**: one or two sentences. It appears under the title, in Google results and in the LinkedIn preview.
   - **Category**: pick one from the list.
   - **Author**: leave as *Arangath* or put a person's name.
   - **Cover image**: click **Choose an image** and upload a landscape picture, at least 1200 pixels wide. This is also the picture LinkedIn shows.
   - **Cover image description**: a few words describing the picture.
   - **Draft**: leave **on** while you are still writing.
   - **Body**: write the article. The toolbar gives you headings, bold, lists, quotes, links and images.
4. Click **Save**. A post marked **Draft** is saved but does **not** appear on the website.
5. When you are happy: switch **Draft** to **off** and click **Save** again. The site rebuilds and the post is live in about a minute.

To take a post down, switch **Draft** back on and save.

## Good to know

- Nothing goes live until **Draft** is off.
- Read time is worked out automatically.
- After the first post is live, the blog page stops showing "First posts coming soon" and shows the post grid with category filters.
- Every post gets its own page title, description, LinkedIn preview and an entry in the site map and the RSS feed at arangath.co.uk/blog/rss.xml.
- If sign-in fails with a "Failed to load config" or "not authorised" message, the GitHub OAuth step above has not been completed, or the account does not have write access to the repository.
