"""Development seed data.

Run from the backend directory:

    .venv/bin/python -m app.seed

Safe to re-run: it clears the existing rows first.
"""

import random

from sqlalchemy import delete, func, select

from app.core.database import SessionLocal, engine
from app.core.security import hash_password
from app.models.like import Like
from app.models.post import Post, post_tags
from app.models.tag import Tag
from app.models.user import User
from app.services.post_service import get_or_create_tags, unique_post_slug

SEED_PASSWORD = "password123"

USERS = [
    ("Grace Hopper", "gracehopper", "Compiler person. Writing about systems and correctness."),
    ("Linus Reyes", "linusreyes", "Linux, networking and everything that runs in a terminal."),
    ("Aisha Rahman", "aisharahman", "Backend engineer. Python, FastAPI and boring reliable databases."),
    ("Marco Silva", "marcosilva", "Frontend developer who cares a lot about accessibility."),
    ("Dana Okafor", "danaokafor", "Platform engineer. Terraform, AWS and too many YAML files."),
    ("Yuki Tanaka", "yukitanaka", "Go and distributed systems. Occasionally Rust."),
    ("Omar Haddad", "omarhaddad", "DevOps. I make deployments boring on purpose."),
    ("Nina Kovacs", "ninakovacs", "Database internals, query plans and indexing."),
]

POSTS = [
    (
        "Understanding Goroutines in Go",
        "Goroutines are cheap, but they are not free. Here is what actually happens when you start one.",
        ["Go", "System Design"],
    ),
    (
        "Building REST APIs with FastAPI",
        "FastAPI gives you validation, serialisation and documentation almost for free. A tour of the parts that matter.",
        ["Python", "FastAPI"],
    ),
    (
        "What I Learned About Docker Networking",
        "Bridge, host and overlay networks explained by way of the mistakes I made in production.",
        ["Docker", "DevOps"],
    ),
    (
        "Vue 3 Composition API Explained",
        "Why the Composition API exists, and how to structure a component once you stop reaching for options.",
        ["Vue", "JavaScript"],
    ),
    (
        "Understanding PostgreSQL Transactions",
        "Isolation levels are not academic trivia. They decide whether your money-moving code is correct.",
        ["Databases"],
    ),
    (
        "Deploying a React Application with AWS CloudFront",
        "A practical walkthrough of an S3 and CloudFront setup, including the cache invalidation trap.",
        ["React", "AWS"],
    ),
    (
        "Introduction to Terraform State",
        "State is the whole product. Understand it before you run your first apply against something real.",
        ["DevOps", "AWS"],
    ),
    (
        "How Nginx Reverse Proxy Works",
        "Upstreams, buffering and the handful of directives that fix ninety percent of proxy problems.",
        ["Linux", "DevOps"],
    ),
    (
        "Understanding JavaScript Closures",
        "Closures are just functions that remember. Once that clicks, a lot of JavaScript stops being surprising.",
        ["JavaScript"],
    ),
    (
        "Getting Started with Linux Processes",
        "Forks, exec, signals and process groups, explained with commands you can run right now.",
        ["Linux"],
    ),
    (
        "Type Narrowing Patterns in TypeScript",
        "Discriminated unions and type guards let you delete most of your defensive checks.",
        ["TypeScript"],
    ),
    (
        "Database Indexing for Application Developers",
        "You do not need to read the source to reason about indexes. You need to read query plans.",
        ["Databases", "System Design"],
    ),
    (
        "Writing Dockerfiles That Build Fast",
        "Layer ordering, cache mounts and multi-stage builds, in the order they will actually help you.",
        ["Docker"],
    ),
    (
        "SQLAlchemy Relationships Without the N+1",
        "Lazy loading is a footgun in a loop. Here is when to reach for selectinload and joinedload.",
        ["Python", "Databases"],
    ),
    (
        "Designing Pagination That Scales",
        "Offset pagination is fine until it isn't. What cursor pagination buys you and what it costs.",
        ["System Design", "Databases"],
    ),
    (
        "Reading Nginx and Systemd Logs Effectively",
        "journalctl has a good interface hiding behind a bad reputation. A short field guide.",
        ["Linux", "DevOps"],
    ),
    (
        "JWT Authentication in Practice",
        "What a JWT is good for, what it is bad for, and the mistakes that keep showing up in reviews.",
        ["System Design", "Python"],
    ),
    (
        "Tailwind CSS Without the Class Soup",
        "Utility classes scale better than people expect, if you are disciplined about extraction.",
        ["JavaScript", "Vue"],
    ),
    (
        "Understanding the Node.js Event Loop",
        "Timers, microtasks and I/O callbacks, in the order Node actually runs them.",
        ["Node.js", "JavaScript"],
    ),
    (
        "A Practical Guide to Git Rebase",
        "Rebase is not dangerous. Rebasing shared history is. Here is where the line sits.",
        ["DevOps"],
    ),
    (
        "Structuring a FastAPI Project",
        "Routers, dependencies and services: a layout that stays readable past ten endpoints.",
        ["FastAPI", "Python"],
    ),
    (
        "What Makes a Good Health Check",
        "A health check that always returns 200 is a liability. What to actually assert.",
        ["System Design", "DevOps"],
    ),
    (
        "Vue Router Navigation Guards in Depth",
        "Guards run in a specific order, and knowing it saves you from redirect loops.",
        ["Vue", "TypeScript"],
    ),
    (
        "Choosing Between MySQL and PostgreSQL",
        "Both are excellent. The interesting differences are operational, not featural.",
        ["Databases"],
    ),
]

PARAGRAPHS = [
    "This is a development seed article. The content exists so the reading view, the "
    "estimated reading time and the typography all have something realistic to render.",
    "Most of the value in understanding a tool like this comes from knowing which of its "
    "defaults you should leave alone. The defaults are usually chosen by people who have "
    "seen far more failure modes than you have, and overriding them without a reason is "
    "how configuration files grow to a thousand lines.",
    "The failure mode worth internalising is the one that only appears under concurrency. "
    "A single request will pass every test you write by hand. The interesting behaviour "
    "shows up when two requests arrive at the same moment and both believe they are the "
    "only one running.",
    "When you do need to reach for something more specialised, prefer the smallest change "
    "that removes the problem. Rewriting the layer is satisfying and almost never the "
    "correct first move. Measure, change one thing, then measure again.",
    "None of this is a substitute for reading the documentation, but it should be enough "
    "to make the documentation legible. Start with the part you are about to depend on, "
    "and come back for the rest when something surprises you.",
]


def build_content(title: str) -> str:
    body = "\n\n".join(PARAGRAPHS)
    return f"## {title}\n\n{body}\n\n### Wrapping up\n\n{PARAGRAPHS[-1]}"


def seed() -> None:
    with SessionLocal() as db:
        # Clear in dependency order so foreign keys stay satisfied.
        db.execute(delete(Like))
        db.execute(post_tags.delete())
        db.execute(delete(Post))
        db.execute(delete(Tag))
        db.execute(delete(User))
        db.commit()

        password_hash = hash_password(SEED_PASSWORD)
        users = [
            User(
                full_name=full_name,
                username=username,
                email=f"{username}@example.com",
                password_hash=password_hash,
                bio=bio,
                avatar_url=None,
            )
            for full_name, username, bio in USERS
        ]
        db.add_all(users)
        db.flush()

        rng = random.Random(20260908)
        posts: list[Post] = []
        for index, (title, excerpt, tag_names) in enumerate(POSTS):
            author = users[index % len(users)]
            post = Post(
                author_id=author.id,
                title=title,
                slug=unique_post_slug(db, title),
                excerpt=excerpt,
                content=build_content(title),
                tags=get_or_create_tags(db, tag_names),
            )
            db.add(post)
            posts.append(post)
        db.flush()

        # Random likes, respecting one like per user per post.
        like_total = 0
        for post in posts:
            likers = rng.sample(users, rng.randint(0, len(users) - 1))
            for user in likers:
                db.add(Like(user_id=user.id, post_id=post.id))
                like_total += 1
        db.commit()

        tag_count = db.scalar(select(func.count(Tag.id))) or 0
        print(
            f"Seeded {len(users)} users, {len(posts)} posts, "
            f"{tag_count} tags and {like_total} likes."
        )
        print(f"Every seeded account uses the password: {SEED_PASSWORD}")


if __name__ == "__main__":
    print(f"Seeding {engine.url.render_as_string(hide_password=True)}")
    seed()
