# Build a Simple Full-Stack Technology Blog Application

Build a complete but intentionally simple **online technology blog platform** where developers and technology enthusiasts can create accounts, publish technical posts, discover other authors, react to posts with likes, and explore user profiles.

The project should feel like a real-world application while keeping the codebase easy to understand, maintain, and extend.

Do **not** over-engineer the application.

---

# 1. Technology Stack

## Frontend

Use:

* Vue.js 3
* TypeScript
* Vite
* Tailwind CSS
* Vue Router
* Pinia for global state management
* Axios for HTTP requests
* VueUse where it provides useful small utilities
* Lucide Vue Next for icons
* Zod for validation if necessary

Prefer Vue 3 Composition API with:

```ts
<script setup lang="ts">
```

Do not use the Options API.

---

## Backend

Use:

* Python
* FastAPI
* SQLAlchemy ORM
* MySQL
* Pydantic
* Alembic for database migrations
* JWT authentication
* Passlib / bcrypt or another appropriate secure password hashing library
* Uvicorn

Keep the FastAPI structure modular but simple.

Do not introduce:

* Redis
* Celery
* message queues
* event-driven architecture
* microservices
* WebSockets
* GraphQL
* Kubernetes
* Docker at this stage

The goal is a clean traditional REST API.

---

# 2. Application Concept

The application is a simple social blogging platform focused specifically on technology-related content.

Users should be able to:

1. Create an account.
2. Log into their account.
3. Create technology-related blog posts.
4. Edit their own blog posts.
5. Delete their own blog posts.
6. Browse posts from other users.
7. Like a post.
8. Unlike a previously liked post.
9. View their own profile.
10. View another user's profile.
11. See all posts belonging to a specific user.

There should be **no commenting system**.

Users only interact with posts through:

```text
Like
Unlike
```

Do not add:

* comments
* replies
* followers
* following
* direct messages
* notifications
* bookmarks
* subscriptions
* paid features

Keep the social functionality intentionally minimal.

---

# 3. Main Application Pages

Create the following frontend pages.

## Public Pages

### Home / Blog Feed

Route:

```text
/
```

Display recently published blog posts.

Each post card should display:

* Author avatar
* Author name
* Username
* Publication date
* Post title
* Short excerpt
* Technology/category tags
* Number of likes
* Like button
* Estimated reading time if easy to calculate

Clicking the title or card should navigate to the blog details page.

Clicking the author should navigate to their profile.

The home page should include a clean header such as:

```text
TechBlog

Home
Explore
Write
Profile
```

Show Login/Register instead of Write/Profile when the user is not authenticated.

---

# 4. Explore Page

Route:

```text
/explore
```

Allow users to browse technology posts.

Include a simple search input.

Search should support:

* post title
* author name
* technology tags

Example tags:

```text
JavaScript
TypeScript
Vue
React
Python
FastAPI
Node.js
Docker
DevOps
AWS
Linux
Databases
System Design
```

Do not build a complex search engine.

A simple database query is enough.

---

# 5. Blog Details Page

Route example:

```text
/posts/:id
```

Display the complete article.

Structure:

```text
Post title

Author information
Publication date
Reading time

Tags

Article content

Like button
Like count

Author mini profile
```

The reading experience should be clean and distraction-free.

The article content area should have a reasonable maximum width such as:

```text
max-w-3xl
```

or similar.

If the logged-in user owns the post, display:

```text
Edit
Delete
```

Do not display these options for other users.

---

# 6. Create Blog Page

Route:

```text
/write
```

This page should only be accessible to authenticated users.

Fields:

```text
Title

Short description / excerpt

Blog content

Technology tags
```

Keep the editor simple.

A normal textarea is acceptable initially.

Do not implement a complex rich-text editor unless it can be added without making the application significantly more complicated.

Possible form:

```text
Title
What's your article about?

Description
Write a short summary...

Tags
Vue, FastAPI, MySQL

Content
Write your article...
```

Include:

```text
Publish Post
```

Validate:

* title required
* title length
* description required
* content required
* reasonable content length
* at least one technology tag if tags are required

---

# 7. Edit Blog Page

Route:

```text
/posts/:id/edit
```

Only the post owner can access this page.

Use the same form component used for creating a blog post if practical.

Allow updating:

* title
* description
* content
* tags

---

# 8. Authentication

Create:

```text
/login
/register
```

## Registration Fields

```text
Full Name
Username
Email
Password
Confirm Password
```

Optional:

```text
Short bio
```

Validation should include:

* valid email
* unique email
* unique username
* password minimum length
* matching password confirmation

Never store plain-text passwords.

Passwords must be securely hashed before storing them.

---

# 9. Login

Fields:

```text
Email or Username
Password
```

After successful login:

* authenticate the user
* store authentication state
* redirect them to the home feed

Use JWT authentication.

Prefer a straightforward implementation.

For example:

```text
access token
```

The backend should validate protected requests.

Do not build refresh-token rotation or complicated authentication infrastructure unless it is truly necessary.

---

# 10. User Profile

Authenticated user profile route:

```text
/profile
```

Public profile route:

```text
/users/:username
```

Profile should display:

```text
Avatar

Full Name

@username

Short bio

Joined date

Number of published posts

Total likes received
```

Under the profile information display:

```text
Posts
```

and show all blog posts written by that user.

For the logged-in user's own profile, show:

```text
Edit Profile
```

Do not show this button when viewing another person's profile.

---

# 11. Edit Profile

Allow users to update:

```text
Full name
Bio
Avatar URL
```

Keep avatar handling simple.

Initially use:

```text
avatar_url
```

instead of building image upload infrastructure.

If no avatar exists, generate a clean fallback avatar using:

* initials
* simple colored circle
* generic user icon

---

# 12. Like / Unlike Feature

Users should be able to like any blog post except there is no need for any additional reaction type.

Only:

```text
Like
Unlike
```

A user should only be able to like the same post once.

Clicking like:

```text
Like → Unlike
```

Clicking again:

```text
Unlike → Like
```

The like count should update immediately in the frontend.

Example:

```text
♡ 14

↓ click

♥ 15
```

If clicked again:

```text
♡ 14
```

The backend must enforce uniqueness.

Do not rely only on frontend state.

---

# 13. Database Design

Use MySQL.

Keep the database schema simple.

## users

Suggested columns:

```text
id
full_name
username
email
password_hash
bio
avatar_url
created_at
updated_at
```

Constraints:

```text
email UNIQUE
username UNIQUE
```

---

## posts

Suggested columns:

```text
id
author_id
title
slug
excerpt
content
created_at
updated_at
```

Relationship:

```text
users
  1
  |
  |
  many
posts
```

Each post belongs to one user.

---

## tags

Suggested columns:

```text
id
name
slug
```

Example:

```text
Vue
FastAPI
Python
Docker
AWS
MySQL
```

---

## post_tags

Many-to-many relationship:

```text
post_id
tag_id
```

Relationship:

```text
posts
   |
   |
post_tags
   |
   |
tags
```

---

## likes

Suggested columns:

```text
id
user_id
post_id
created_at
```

Create a unique constraint:

```text
UNIQUE(user_id, post_id)
```

This ensures a user cannot like the same post multiple times.

---

# 14. Database Relationships

Conceptually:

```text
User
 │
 ├──── has many ──── Posts
 │
 └──── has many ──── Likes

Post
 │
 ├──── belongs to ── User
 │
 ├──── has many ──── Likes
 │
 └──── has many ──── Tags
```

---

# 15. Backend Folder Structure

Use a structure similar to:

```text
backend/
│
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── tag.py
│   │   └── like.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── post.py
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── posts.py
│   │   └── likes.py
│   │
│   └── services/
│       ├── auth_service.py
│       └── post_service.py
│
├── alembic/
├── requirements.txt
├── alembic.ini
└── .env
```

Do not create repository, service, controller and data-access layers for every feature unless they provide an obvious benefit.

Avoid unnecessary abstractions.

---

# 16. Frontend Folder Structure

Use something similar to:

```text
frontend/
│
├── src/
│   ├── assets/
│   │
│   ├── components/
│   │   ├── layout/
│   │   ├── posts/
│   │   ├── profile/
│   │   └── common/
│   │
│   ├── views/
│   │   ├── HomeView.vue
│   │   ├── ExploreView.vue
│   │   ├── LoginView.vue
│   │   ├── RegisterView.vue
│   │   ├── CreatePostView.vue
│   │   ├── EditPostView.vue
│   │   ├── PostDetailsView.vue
│   │   └── UserProfileView.vue
│   │
│   ├── stores/
│   │   └── auth.ts
│   │
│   ├── services/
│   │   ├── api.ts
│   │   ├── auth.service.ts
│   │   ├── post.service.ts
│   │   └── user.service.ts
│   │
│   ├── types/
│   │   ├── user.ts
│   │   └── post.ts
│   │
│   ├── router/
│   │   └── index.ts
│   │
│   ├── App.vue
│   └── main.ts
│
├── package.json
└── vite.config.ts
```

Keep components reusable without splitting every tiny UI element into its own component.

---

# 17. REST API Design

Use `/api/v1` as the API prefix.

Example:

```text
/api/v1
```

---

## Authentication

### Register

```http
POST /api/v1/auth/register
```

Body:

```json
{
  "full_name": "John Doe",
  "username": "johndoe",
  "email": "john@example.com",
  "password": "password123"
}
```

---

### Login

```http
POST /api/v1/auth/login
```

---

### Current User

```http
GET /api/v1/auth/me
```

Requires authentication.

---

# 18. Posts API

## Get Posts

```http
GET /api/v1/posts
```

Support simple pagination:

```text
?page=1&limit=10
```

Optional:

```text
?search=fastapi
?tag=python
```

---

## Get Single Post

```http
GET /api/v1/posts/{post_id}
```

---

## Create Post

```http
POST /api/v1/posts
```

Authentication required.

---

## Update Post

```http
PUT /api/v1/posts/{post_id}
```

Only the owner can update it.

---

## Delete Post

```http
DELETE /api/v1/posts/{post_id}
```

Only the owner can delete it.

---

# 19. Like API

Use either:

```http
POST /api/v1/posts/{post_id}/like
DELETE /api/v1/posts/{post_id}/like
```

or a single toggle endpoint if preferred.

Separate endpoints are preferred because they clearly represent the actions.

Example:

```http
POST /api/v1/posts/12/like
```

Response:

```json
{
  "liked": true,
  "like_count": 15
}
```

Unlike:

```http
DELETE /api/v1/posts/12/like
```

Response:

```json
{
  "liked": false,
  "like_count": 14
}
```

---

# 20. User APIs

Get a public profile:

```http
GET /api/v1/users/{username}
```

Get posts from that user:

```http
GET /api/v1/users/{username}/posts
```

Update current user's profile:

```http
PUT /api/v1/users/me
```

---

# 21. Authorization Rules

Backend authorization is mandatory.

Do not depend on frontend restrictions.

Examples:

A user can:

```text
create their own post
edit their own post
delete their own post
edit their own profile
like another user's post
unlike a previously liked post
```

A user cannot:

```text
edit someone else's post
delete someone else's post
edit someone else's profile
like the same post multiple times
```

Return appropriate HTTP status codes such as:

```text
200
201
204
400
401
403
404
409
422
```

---

# 22. Frontend State Management

Use Pinia primarily for authentication.

Example state:

```ts
user
token
isAuthenticated
loading
```

Example actions:

```ts
login()
register()
logout()
fetchCurrentUser()
```

Do not put every API response in Pinia.

For example, posts belonging only to a single page can remain local component state.

---

# 23. Axios Setup

Create one central Axios instance:

```text
src/services/api.ts
```

Example responsibilities:

```text
base URL
authorization header
basic response/error handling
```

Avoid repeating the full backend URL throughout the frontend.

Use environment variables such as:

```text
VITE_API_URL=http://localhost:8000/api/v1
```

---

# 24. UI Design Direction

The application should feel:

```text
Modern
Clean
Developer-focused
Professional
Minimal
Comfortable
Slightly dim
```

Avoid an extremely white interface.

Avoid pure black.

The interface should sit somewhere between light mode and dark mode.

Think of:

```text
GitHub
Linear
Vercel
Dev.to
Medium
modern developer dashboards
```

but do not directly copy any specific website.

---

# 25. Suggested Color System

Use a slightly dim neutral interface.

Example:

### Main Background

```text
#111827
```

or:

```text
slate-950 / slate-900
```

### Card Background

```text
#1F2937
```

or:

```text
slate-800
```

### Secondary Background

```text
#172033
```

### Primary Accent

Use a soft indigo/blue:

```text
#6366F1
```

### Accent Hover

```text
#818CF8
```

### Primary Text

```text
#F1F5F9
```

### Secondary Text

```text
#94A3B8
```

### Borders

```text
rgba(148, 163, 184, 0.15)
```

### Success

```text
emerald
```

### Error

```text
red / rose
```

Do not overuse the primary accent color.

It should mainly appear on:

```text
buttons
links
active navigation
like interactions
focus states
small highlights
```

---

# 26. UI Style

Use:

* rounded corners
* subtle borders
* subtle shadows
* comfortable spacing
* smooth hover transitions
* good typography
* clear hierarchy
* spacious blog layouts

Example cards:

```text
rounded-xl
border
border-slate-800
bg-slate-900/70
```

Do not use excessive:

* gradients
* glassmorphism
* huge shadows
* animations
* glowing effects
* neon colors

The UI should feel calm and professional.

---

# 27. Navigation

Desktop header example:

```text
[TechBlog]

Home
Explore

                      Search...

Write
Profile
```

When logged out:

```text
Login
Create Account
```

Mobile:

Use a simple responsive navigation menu.

---

# 28. Blog Card Design

Example structure:

```text
┌──────────────────────────────────────────────┐

  [Avatar] John Doe
           @johndoe · 2 hours ago

  Building REST APIs with FastAPI

  FastAPI makes building Python APIs simple while
  providing automatic validation and documentation...

  [Python] [FastAPI] [Backend]

  ♡ 24 likes                         5 min read

└──────────────────────────────────────────────┘
```

Use subtle hover behavior.

Avoid excessive card decoration.

---

# 29. Profile Design

Example:

```text
              [Avatar]

             John Doe
             @johndoe

  Backend engineer interested in Python,
  APIs, distributed systems and DevOps.

      16 Posts            421 Likes

             Edit Profile

-------------------------------------------------

Posts

[Post card]

[Post card]

[Post card]
```

For another user's profile, remove:

```text
Edit Profile
```

---

# 30. Loading States

Provide proper loading indicators.

Examples:

```text
post card skeletons
profile skeleton
button spinner
```

Do not leave blank screens while API calls are happening.

---

# 31. Empty States

Create useful empty states.

Examples:

No posts:

```text
No posts yet.

Start sharing something you've learned.
```

No search results:

```text
No articles found for "Kubernetes".
```

User has no posts:

```text
This user hasn't published anything yet.
```

---

# 32. Error States

Display friendly errors.

Example:

```text
Unable to load posts.
Please try again.
```

Forms should show validation errors underneath the relevant input.

Avoid using browser `alert()`.

---

# 33. Confirmation Modal

Before deleting a blog post, display a confirmation dialog:

```text
Delete this article?

This action cannot be undone.

Cancel
Delete
```

Use a proper modal instead of `window.confirm()`.

---

# 34. Responsive Design

The complete application must work properly on:

```text
mobile
tablet
desktop
```

Use responsive Tailwind utilities.

Avoid horizontal scrolling.

Blog articles should remain comfortable to read on mobile.

---

# 35. Accessibility

Basic accessibility requirements:

* semantic HTML
* proper labels
* keyboard accessible buttons
* visible focus states
* adequate contrast
* `aria-label` for icon-only buttons
* proper heading structure

---

# 36. Icons

Use:

```text
lucide-vue-next
```

Suggested icons:

```text
Home
Compass
PenLine
User
Heart
LogOut
Search
Settings
Trash2
Pencil
Calendar
Clock
Tag
ChevronDown
Menu
X
```

Do not use random emoji instead of UI icons.

---

# 37. Security

At minimum implement:

* password hashing
* JWT validation
* protected backend endpoints
* proper authorization
* input validation using Pydantic
* SQLAlchemy queries instead of raw SQL where unnecessary
* environment variables for secrets
* appropriate CORS configuration
* unique database constraints
* protection against users modifying other users' resources

Never hard-code:

```text
database credentials
JWT secrets
production URLs
passwords
```

Use `.env`.

Example backend:

```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/tech_blog
JWT_SECRET=change-me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
FRONTEND_URL=http://localhost:5173
```

---

# 38. Backend Error Format

Try to maintain a consistent API response format.

Example error:

```json
{
  "detail": "Post not found"
}
```

or another simple consistent structure.

Do not create an overly complicated API response wrapper.

---

# 39. Pagination

Implement basic pagination on the feed.

Example:

```text
GET /posts?page=1&limit=10
```

Possible response:

```json
{
  "items": [],
  "page": 1,
  "limit": 10,
  "total": 57,
  "total_pages": 6
}
```

On the frontend provide:

```text
Previous
1
2
3
Next
```

or a simple:

```text
Load More
```

Either approach is acceptable.

Prefer the simpler implementation.

---

# 40. Post Response Model

A post API response should provide enough information that the frontend doesn't need many additional requests.

Example:

```json
{
  "id": 12,
  "title": "Getting Started with FastAPI",
  "slug": "getting-started-with-fastapi",
  "excerpt": "FastAPI makes building Python APIs...",
  "content": "...",
  "created_at": "2026-09-08T12:00:00",
  "updated_at": "2026-09-08T12:00:00",
  "author": {
    "id": 4,
    "full_name": "John Doe",
    "username": "johndoe",
    "avatar_url": null
  },
  "tags": [
    {
      "id": 1,
      "name": "Python"
    },
    {
      "id": 2,
      "name": "FastAPI"
    }
  ],
  "like_count": 24,
  "liked_by_current_user": true
}
```

This allows the frontend to render the post efficiently.

---

# 41. Development Priorities

Build the project in phases.

## Phase 1 — Backend Foundation

Implement:

```text
FastAPI setup
MySQL connection
SQLAlchemy
Alembic
environment configuration
basic application structure
```

Verify database connectivity before proceeding.

---

## Phase 2 — Authentication

Implement:

```text
User model
Register endpoint
Login endpoint
JWT generation
JWT validation
GET /auth/me
```

Test authentication completely before proceeding.

---

## Phase 3 — Posts

Implement:

```text
Create post
Get posts
Get individual post
Update post
Delete post
```

Verify ownership authorization.

---

## Phase 4 — Likes

Implement:

```text
Like post
Unlike post
Like count
Current user's like state
```

Verify the database prevents duplicate likes.

---

## Phase 5 — Profiles

Implement:

```text
Get profile
Edit own profile
Get posts by username
Profile statistics
```

---

## Phase 6 — Frontend Foundation

Set up:

```text
Vue
TypeScript
Tailwind
Vue Router
Pinia
Axios
Lucide icons
```

Create the common layout.

---

## Phase 7 — Authentication UI

Create:

```text
Login
Register
Auth store
Protected routes
Logout
```

Connect them to the real backend.

---

## Phase 8 — Blog UI

Create:

```text
Home feed
Post cards
Post details
Create post
Edit post
Delete post
```

---

## Phase 9 — Social Features

Connect:

```text
Like
Unlike
Profiles
Other users' posts
Explore/search
```

---

## Phase 10 — Polish

Finish:

```text
responsive design
loading states
empty states
error states
form validation
accessibility
UI consistency
```

---

# 42. Testing

Keep testing practical.

Backend should test important flows such as:

```text
Register user
Login
Invalid login
Create post
Unauthenticated create attempt
Update own post
Cannot update another user's post
Delete own post
Like post
Duplicate like prevention
Unlike post
Get user profile
```

Use FastAPI's testing utilities with pytest.

Frontend tests are optional initially.

Prioritize getting the complete application functionality working correctly first.

---

# 43. Seed Data

Create optional development seed data containing:

```text
5-10 users
15-30 blog posts
common technology tags
random likes
```

Use realistic technology-related post titles.

Examples:

```text
Understanding Goroutines in Go

Building REST APIs with FastAPI

What I Learned About Docker Networking

Vue 3 Composition API Explained

Understanding PostgreSQL Transactions

Deploying a React Application with AWS CloudFront

Introduction to Terraform State

How Nginx Reverse Proxy Works

Understanding JavaScript Closures

Getting Started with Linux Processes
```

This will make the interface easier to test.

---

# 44. Important Engineering Principles

Throughout implementation prioritize:

```text
Simplicity
Readability
Maintainability
Consistency
Good naming
Clear separation of concerns
```

Avoid:

```text
premature optimization
huge abstraction layers
generic base classes
microservices
complex design patterns
unnecessary dependencies
unnecessary state management
```

This is a learning-focused project that should still resemble a realistic production application.

A junior or mid-level developer should be able to open the repository and quickly understand:

```text
where authentication happens
where routes are defined
where database models live
where API requests happen
where frontend state lives
how a post is created
how likes work
how users are authorized
```

---

# 45. Expected Final Experience

A visitor should be able to open the application and immediately browse technology articles.

After creating an account they should be able to:

```text
Login
   ↓
Browse feed
   ↓
Read articles
   ↓
Like articles
   ↓
Write their own article
   ↓
See it on their profile
   ↓
Visit another author's profile
   ↓
Browse that author's articles
```

The final product should feel like a very lightweight combination of:

```text
Medium
Dev.to
Hashnode
```

but much simpler.

The focus is not on building a feature-heavy social network.

The focus is building a clean and realistic full-stack application using:

```text
Vue 3 + TypeScript
FastAPI
MySQL
Tailwind CSS
```

with strong fundamentals in:

```text
authentication
REST API design
database relationships
authorization
frontend/backend integration
state management
responsive UI
```

Build the core functionality first, test each feature properly, and only then polish the interface.
