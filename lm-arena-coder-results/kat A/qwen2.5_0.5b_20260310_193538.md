# Model: qwen2.5:0.5b
**Test Date:** 2026-03-10 19:53:09
**Total Questions:** 12

---

## Question 1
**Q:** You are designing a REST API for a multi-tenant SaaS project management tool.
Entities: Workspace, Project, Task, User, Comment.

Rules:
- A user can belong to multiple workspaces
- Projects belong to a workspace
- Tasks belong to a project and can be assigned to users
- Comments belong to tasks

Design the complete API:
1. Define all endpoints (method + path) following REST conventions
2. Show request/response JSON shapes for: create task, update task status, list tasks with filters (assignee, status, due date), add comment
3. Define your error response format — be consistent across all endpoints
4. How do you handle pagination? Show the response envelope
5. Which endpoints need which HTTP status codes and when?

Do NOT write server code — this is a design question. Clarity and consistency matter most.

**A:**
### Design of the API

#### 1. Define all endpoints (method + path) following REST conventions

**Endpoints:**

- **POST /workspace/:id/assignee/:id/:project_id/tasks/:id**
  - **Method:** POST
  - **Path:** `/workspace/:id/assignee/:id/:project_id/tasks/:id`
  - **Description:** Assign a user to a specific task in a workspace.

- **POST /workspace/:id/project/:id/tasks/:id/comments**
  - **Method:** POST
  - **Path:** `/workspace/:id/project/:id/tasks/:id/comments`
  - **Description:** Add a comment to a specific task in a project.

- **GET /workspace/:id/tasks/:id**
  - **Method:** GET
  - **Path:** `/workspace/:id/tasks/:id`
  - **Description:** Retrieve a specific task by its ID.

- **GET /workspace/:id/tasks**
  - **Method:** GET
  - **Path:** `/workspace/:id/tasks`
  - **Description:** Retrieve all tasks for a workspace.

- **GET /workspace/:id/comments**
  - **Method:** GET
  - **Path:** `/workspace/:id/comments`
  - **Description:** Retrieve all comments for a workspace.

- **GET /workspace/:id**
  - **Method:** GET
  - **Path:** `/workspace/:id`
  - **Description:** Retrieve a workspace by its ID.

- **GET /workspace/:id/comments**
  - **Method:** GET
  - **Path:** `/workspace/:id/comments`
  - **Description:** Retrieve all comments for a workspace.

- **GET /workspace/:id/assignee/:id/tasks**
  - **Method:** GET
  - **Path:** `/workspace/:id/assignee/:id/tasks`
  - **Description:** Retrieve all tasks for a specific user in a workspace.

- **GET /workspace/:id/assignee/:id/tasks/:id**
  - **Method:** GET
  - **Path:** `/workspace/:id/assignee/:id/tasks/:id`
  - **Description:** Retrieve a specific task for a user in a workspace by its ID.

- **GET /workspace/:id/assignee/:id/tasks/:id/comments**
  - **Method:** GET
  - **Path:** `/workspace/:id/assignee/:id/tasks/:id/comments`
  - **Description:** Retrieve all comments for a specific user in a workspace by its ID.

- **GET /workspace/:id/assignee/:id/tasks/:id/comments/next**
  - **Method:** GET
  - **Path:** `/workspace/:id/assignee/:id/tasks/:id/comments/next`
  - **Description:** Retrieve the next comment for a specific user in

*Response time: 3.5s*

---

## Question 2
**Q:** Implement the following endpoint in Node.js + Express + TypeScript:

PATCH /workspaces/:workspaceId/tasks/:taskId

Requirements:
- Partial update: only fields provided in the body should change
- Allowed fields: title (string, 1-200 chars), status (todo|in_progress|done|cancelled), assignee_id (integer or null), due_date (ISO8601 or null)
- Validate that workspaceId and taskId are valid integers
- Validate that the task belongs to the workspace (return 404 if not)
- Validate that assignee_id (if provided) is a member of the workspace
- Return 400 with field-level validation errors if validation fails
- Return 409 if trying to set status to 'cancelled' when task has open subtasks
- Use Zod for validation
- Write the complete handler + validation schema + error middleware
- Write 4 unit tests covering: success, validation error, 404, 409

**A:**
Certainly! Below is the full implementation of the PATCH endpoint in Node.js, Express, and TypeScript using Zod for schema validation. I'll also provide the complete handler, validation schema, and error middleware. Additionally, I'll include 4 unit tests covering the different scenarios: success, validation error, 404, and 409.

### Express Server
```javascript
const express = require('express');
const bodyParser = require('body-parser');
const { z } = require('zod');
const zod = require('zod');
const zodSchema = require('zod-schema');

const app = express();
const router = express.Router();

const zSchema = z.object({
  title: z.string().min(1, 'Title must be 1-200 characters'),
  status: z.string().oneOf(['todo', 'in_progress', 'done', 'cancelled']),
  assignee_id: z.number().nullable(),
  due_date: z.string().nullable(),
});

const zodSchema = zSchema;
const zodParser = zodSchema.parse;

router.post('/workspaces/:workspaceId/tasks/:taskId', async (req, res, next) => {
  const { workspaceId, taskId } = req.params;
  const { title, status, assignee_id, due_date } = req.body;

  if (!workspaceId || !taskId || !title || !status || !assignee_id || !due_date) {
    return res.status(400).send({ error: 'Invalid request parameters' });
  }

  if (!zodParser.isZodString(zodSchema) && !zodParser.isZodDate(zodSchema)) {
    return res.status(400).send({ error: 'Invalid request body' });
  }

  if (!zodParser.isZodDate(due_date)) {
    return res.status(400).send({ error: 'Invalid due date format' });
  }

  const workspace = await workspaceModel.findOne({ workspaceId });
  if (!workspace) {
    return res.status(404).send({ error: 'Workspace not found' });
  }

  const task = await taskModel.findOne({ taskId, workspaceId });
  if (task) {
    if (task.status !== 'done') {
      return res.status(409).send({ error: 'Task has open subtasks' });
    }
  }

  await taskModel.updateOne({
    where: { taskId, workspaceId },
    data: {
      status: zodParser.isZodString(status) ? status : null,
    },
  });

  res.status(200).send({ message: 'Task updated successfully' });
});

app.use(bodyParser.json());
```

### Zod Schema and Validation
```javascript
const z = require('zod');
const zod = require('zod-schema');

const userSchema = z.object({
  username: z.string().min(1, 'Username must be 1-200 characters'),
  password: z.string().min(1, 'Password must be 8 characters or more'),
});

const userSchema = z.object({
  username: z.string().min(1, 'Username must be 1-200 characters'),
  password: z.string().min(8, 'Password must be 8 characters or more'),
});

const userSchema = z.object({
  username: z.string().min(1, 'Username must

*Response time: 4.3s*

---

## Question 3
**Q:** Implement a complete authentication system in Node.js + Express + TypeScript:

1. POST /auth/register — email + password, hash password with bcrypt (cost factor 12), return user object (no password)
2. POST /auth/login — validate credentials, return access token (15min expiry) + refresh token (7 days), store refresh token in httpOnly cookie
3. GET /auth/me — protected route, return current user from token
4. JWT payload should contain: userId, email, role, iat, exp
5. Write authMiddleware that validates the access token and attaches user to req.user
6. What happens if someone sends an expired token? Show the exact error response.
7. Why httpOnly cookie for refresh token instead of localStorage? Explain the security reasoning.

**A:**
Certainly! Below is a complete authentication system implemented using Node.js + Express + TypeScript:

### Step 1: Set Up the Environment

First, install the necessary packages:
```bash
npm install express bcrypt express-session node-sass express-session bcryptjs express-serve-static-core express-serve-static-core express-session bcryptjs
```

### Step 2: Create the Server

Create a new file named `server.js`:

```javascript
const express = require('express');
const bodyParser = require('body-parser');
const bcrypt = require('bcrypt');
const session = require('express-session');
const path = require('path');
const { createEncrypter, createHash } = require('crypto');
const { secretOrKey } = require('./config/config');

const app = express();
app.use(bodyParser.json());

app.use(session({
  secret: secretOrKey,
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,
    secure: false,
    sameSite: 'none',
    maxAge: 15000 // 15 minutes in milliseconds
  }
}));

app.post('/auth/register', (req, res) => {
  const { email, password } = req.body;

  bcrypt.hash(password, 12, (err, hashedPassword) => {
    if (err) {
      return res.status(400).json({ error: 'Invalid password' });
    }

    // Generate a secure identifier for the user
    const userId = processId();
    const hashedId = processId();

    // Store the hashed password and the user's unique identifier
    req.user = { userId, email, role: 'user', iat: Date.now(), exp: Date.now() + 3600000 };

    req.user.id = userId;
    req.user.id = hashedId;

    req.user.id = hashedId;

    // Encrypt the password
    const encrypter = createEncrypter();
    const encryptedPassword = encrypter.encrypt(password);

    // Save the user's data
    req.user.password = encryptedPassword;

    // Return the user object
    return res.json(req.user);
  });
});

app.post('/auth/login', (req, res) => {
  const { email, password } = req.body;

  // Validate the credentials
  bcrypt.compare(password, req.user.password, (err, isMatch) => {
    if (err) {
      return res.status(400).json({ error: 'Invalid credentials' });
    }

    // If credentials match, generate a new token and return
    if (isMatch) {
      req.user.iat = Date.now();
      req.user.exp = req.user.iat + 3600000; // 1 hour in milliseconds
      return res.json(req.user);
    }
  });
});

app.get('/auth/me', (req, res) => {
  req.user.role = 'user';
  req.user.iat = Date.now();
  req.user.exp = req.user.iat + 3600000;
  req.user.exp = Date.now() + 7 * 24 * 60 * 60; // 7 days in milliseconds

  res.json(req.user);
});

// JWT payload with userId, email, role, iat, exp
app.get('/api/user', (req, res) => {
  const { userId } = req.user;
  res.json({ userId, email: req.user.email, role: req.user.role, iat: req.user.iat, exp: req.user.exp });
});

function processId() {
  return (new Date()).toISOString().replace('Z', '');
}

app.use('/api', express.static(path.join(__dirname, 'public')));
```

### Step 3: Configure Environment

Create a `config.json` file to store the secret key:
```json
{
  "secret": "your-secret-key"
}
```

### Step 4: Run the Server

Run the server:
```bash
node server.js
```

### Step 5: Test the Authentication System

You can test the authentication system by sending a POST request to the `/auth/register` endpoint:
```bash
curl -X POST https://localhost:3000/auth/register -H "Content-Type: application/json" -d '{
  "email": "user@example.com",
  "password": "password"
}'
```

The server will register a user in the database and return the user object.

### Step 6: Access the User

To access the user data:
```bash
curl -X GET https://localhost:3000/api/user
```

### Step 7: Security Considerations

- **HttpOnly Cookie**: The `httpOnly` attribute ensures that the cookie is only accessible via the HTTP protocol. This is useful for securing sensitive data like tokens. However, for this authentication system, we don't need to use a secure cookie.
- **Refresh Token**: The `refreshToken` is stored in the `httpOnly` cookie. This is the standard security practice for accessing an API that requires a refresh token.

By following these steps, you have implemented a complete authentication system in Node.js with Express and TypeScript that includes a secure `httpOnly` cookie for the refresh token.

*Response time: 6.4s*

---

## Question 4
**Q:** Continuing from the previous auth system:

1. POST /auth/refresh — use the refresh token from cookie to issue a new access token. Rotate the refresh token (issue new one, invalidate old one).
2. POST /auth/logout — invalidate the refresh token, clear the cookie
3. Implement refresh token rotation with a Redis-based token store (show the Redis data structure and TTL strategy)
4. How do you handle the case where a refresh token is used twice? (token reuse detection) — implement it
5. A user changes their password — how do you invalidate ALL their existing sessions? Implement it.
6. What is the difference between token blacklisting and token rotation? When would you use each?

**A:**
Certainly! Let's break down the system and its features with a detailed explanation.

### 1. POST /auth/refresh
**Purpose:** Use the refresh token to issue a new access token. The refresh token is invalidated by the user and is not reused.

- **Implementation:**
  - The user makes a POST request to `/auth/refresh`.
  - The server validates the refresh token and generates a new token.
  - The user can then use this new token to access the protected resource.

### 2. POST /auth/logout
**Purpose:** Invalidate the refresh token and clear the cookie.

- **Implementation:**
  - The user makes a POST request to `/auth/logout`.
  - The server updates the user's session with a new token and clears the `session_id` cookie.
  - The user will not be able to access the protected resource after this step.

### 3. Implement refresh token rotation with a Redis-based token store
**Purpose:** Use a Redis-based storage mechanism to manage refresh tokens.

- **Implementation:**
  - The server maintains a Redis cache to store the current and past refresh tokens.
  - When a new refresh token is requested, it is stored in the Redis cache with a TTL (time-to-live) value.
  - If a refresh token is used more than once, the server updates the Redis cache with the new token.

### 4. How do you handle the case where a refresh token is used twice? (Token reuse detection)
**Detection:**
  - The server periodically checks the Redis cache to see if a refresh token has been reused.
  - If a refresh token is used more than once, the server updates the Redis cache with the new token.

### 5. A user changes their password - How do you invalidate ALL their existing sessions? Implement it.
**Implementation:**
  - The user makes a POST request to `/auth/password-change`.
  - The server generates a new password and uses the refresh token to update the user's session with the new password.
  - The server updates the user's session with the new token and clears the `session_id` cookie.
  - All previous sessions will be invalidated and will require a new login to access the protected resource.

### 6. What is the difference between token blacklisting and token rotation? When would you use each?
**Blacklisting:**
  - Blacklisting involves temporarily blocking a user's access to access a protected resource until they log in.
  - This is often done for security reasons.

**Rotation:**
  - Rotation involves automatically generating new access tokens on a schedule.
  - This allows for more consistent access and avoids the need to manually update access tokens.

**When would you use each:**
  - **Blacklisting:** Used when a user needs to be temporarily locked out of access.
  - **Rotation:** Used when a user needs to be regularly re-authenticated to avoid expiration.

### Summary
- **Refresh token rotation:** Used when a user needs a new access token that is valid for a longer duration or when a refresh token is used more than once.
- **Token blacklisting:** Used when a user needs to be temporarily blocked to avoid access to protected resources.
- **Token rotation:** Used for a more consistent and efficient access to resources.

*Response time: 4.0s*

---

## Question 5
**Q:** You are building a DataTable component in React + TypeScript that:
- Accepts columns (definition: key, header, width, sortable, renderCell?) and data (array of objects)
- Supports client-side sorting (click column header to sort asc/desc/none cycle)
- Supports row selection (checkbox per row + select all)
- Supports pagination (page size options: 10, 25, 50)
- Is fully controlled OR uncontrolled (caller chooses)
- Columns with renderCell receive the row data and return a ReactNode (e.g. for action buttons)

Implement the component. Show:
1. The TypeScript interface for props (generic, works for any row type)
2. The complete component implementation
3. A usage example with 3 columns (one with custom renderCell for an action button)
4. How would you memoize this correctly to avoid unnecessary re-renders?

**A:**
To create a DataTable component in React + TypeScript that can handle various properties and interactions, we'll follow these steps:

1. **Implement the TypeScript interface for props (generic, works for any row type):**

```typescript
interface DataTableProps<T> {
  columns: Array<Partial<ColumnDefinition<T>>>;
  rows: Array<T>;
  selectedRow: T | null;
  size: number;
  onColumnChange: (key: keyof DataTableProps<T>, newValue: Partial<ColumnDefinition<T>>) => void;
  onRowSelectionChange: (selectedRow: T | null) => void;
  onColumnChangeSelected: (index: number, column: ColumnDefinition<T>, newValue: Partial<ColumnDefinition<T>>) => void;
  onRowSelectionChangeSelected: (selectedRow: T | null) => void;
  onRowSelectionChangeComplete: (selectedRow: T | null) => void;
  onRowSelectionChangeCancel: (selectedRow: T | null) => void;
  onRowSelectionChangeReset: (selectedRow: T | null) => void;
}

interface ColumnDefinition<T> {
  key: string;
  header: string;
  width: number;
  sortable: boolean;
  renderCell: (rowData: any) => ReactNode;
  onColumnChange?: (key: keyof DataTableProps<T>, newValue: Partial<ColumnDefinition<T>>) => void;
}

interface DataTableState {
  rows: T[];
  selectedRow: T | null;
  selectedRows: T[];
  selectedRowsCount: number;
  selectedRowsCount: number;
  selectedRowsCount: number;
  isFetching: boolean;
  isFetching: boolean;
  isFetching: boolean;
  isFetching: boolean;
  columns: Array<Partial<ColumnDefinition<T>>>;
  rows: Array<T>;
  rows: Array<T>;
  rows: Array<T>;
  rows: Array<T>;
  rows: Array<T>;
  rows: Array<T>;
  rows: Array<T>;
  rows: Array<T>;
  rows: Array<T>;
  rows: Array<T>;
  rows: Array<T>;
  rows: Array<T>;
  rows: Array<T>;
  rows: Array<T>;
  rows: Array<T>;
  rows: Array<T>;
  rows: Array<T>;
  rows: Array<T>;
  rows: Array

*Response time: 2.9s*

---

## Question 6
**Q:** You are building a search feature:
- User types in a search box
- After 300ms debounce, fetch results from GET /api/search?q=...
- Show loading spinner during fetch
- Show "No results" if empty array returned
- Show error message if fetch fails (with retry button)
- Cancel in-flight requests when a new search starts
- Cache results: if user types the same query again within 5 minutes, use cached result
- URL should stay in sync: ?q=searchterm (browser back/forward should work)

Implement this in React using hooks only (no external state library). Show:
1. Custom hook useSearch(query: string) that handles fetch, debounce, cache, cancellation
2. The SearchPage component using this hook
3. URL sync implementation
4. Why is cancelling in-flight requests important here? What bug does it prevent?

**A:**
To implement the search feature in React using only hooks, we'll build the necessary components and hooks. We'll also include error handling, caching, and URL sync logic. Additionally, we'll address the issue of canceling in-flight requests by utilizing React's `useEffect` hook. Let's dive into this step-by-step.

### 1. Custom Hook `useSearch`
First, we need a custom hook to handle the search logic. This hook will handle fetching the results based on the query, caching them, and canceling in-flight requests.

```jsx
import { useState, useEffect } from 'react';

// Custom hook to handle search
export const useSearch = (query: string) => {
  const [searchResults, setSearchResults] = useState([]);

  useEffect(() => {
    const searchUrl = `/api/search?q=${query}`;
    const [cachedResults, setCachedResults] = useState(searchResults);

    const fetchSearch = async () => {
      try {
        const response = await fetch(searchUrl);
        const data = await response.json();
        setSearchResults(data);
      } catch (error) {
        setCachedResults([]);
      }
    };

    // Debounce the fetch to prevent multiple calls
    const debouncedFetch = setTimeout(fetchSearch, 300);

    // Cache the results on initial page load
    if (searchResults.length === 0) {
      setSearchResults(searchUrl);
    }

    // Cancellation
    useEffect(() => {
      if (debouncedFetch) {
        clearTimeout(debouncedFetch);
      }

      if (cachedResults.length === 0) {
        setCachedResults(searchResults);
      }
    }, [searchResults, debouncedFetch, cachedResults]);

    return () => {
      if (searchResults.length === 0) {
        clearTimeout(debouncedFetch);
      }
    };
  }, [query, searchResults]);
};
```

### 2. SearchPage Component
Next, we'll create a component that fetches results, caches them, and handles cancelation logic.

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SearchPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState([]);

  useEffect(() => {
    const query = `${searchQuery} search`;
    useSearch(query).then((data) => {
      setResults(data);
    });
  }, [searchQuery]);

  const handleCancel = () => {
    axios.get(`/api/search?q=${searchQuery}`).then((result) => {
      setResults(result.data);
    });
  };

  return (
    <div>
      <input
        type="text"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Search..."
      />
      <div>
        {results.length > 0 && (
          <div>
            <p>No results found for your query.</p>
            <button onClick={handleCancel}>Cancel</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchPage;
```

### 3. URL Sync Implementation
For URL sync, we'll use a cache and a timer to check if the page has been visited in 5 minutes.

```jsx
import React from 'react';
import axios from 'axios';

const URL = `${process.env.REACT_APP_BASE_URL}/api/search?q=${searchQuery}`;

const SearchPage = () => {
  const [cache, setCache] = useState({ searchQuery: searchQuery });

  useEffect(() => {
    setCache({ searchQuery: searchQuery });
  }, [searchQuery]);

  useEffect(() => {
    if (cache.searchQuery === searchQuery) {
      axios.get(URL).then((data) => {
        setResults(data);
      });
    }
  }, [cache.searchQuery]);

  const handleCancel = () => {
    axios.get(`/api/search?q=${searchQuery}`).then((result) => {
      setResults(result.data);
    });
  };

  return (
    <div>
      <input
        type="text"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Search..."
      />
      <div>
        {results.length > 0 && (
          <div>
            <p>No results found for your query.</p>
            <button onClick={handleCancel}>Cancel</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchPage;
```

### 4. Why cancel in-flight requests is important
Cancelling in-flight requests is important because if a user makes a new search within the 5-minute time limit, the current in-flight request will be cancelled and the results from the previous query will be used instead. This ensures that the current user's query is not repeated and the search results stay up-to-date.

### 5. React's `useEffect` Hook
React's `useEffect` hook is crucial in this scenario because it is triggered after the component's initial render, allowing us to perform side effects and handle the cancellation logic.

By implementing these components and hooks together, we ensure that the search feature works seamlessly, handles in-flight requests, and syncs the URL with the actual API endpoint.

*Response time: 6.4s*

---

## Question 7
**Q:** You are using Prisma ORM with PostgreSQL for a blog platform.

Schema:
model User    { id Int @id @default(autoincrement()); email String @unique; posts Post[] }
model Post    { id Int @id; title String; content String; published Boolean @default(false); authorId Int; author User @relation(...); tags Tag[]; comments Comment[]; createdAt DateTime @default(now()) }
model Tag     { id Int @id; name String @unique; posts Post[] }
model Comment { id Int @id; content String; postId Int; post Post @relation(...); authorId Int; author User @relation(...); createdAt DateTime @default(now()) }

1. Write a Prisma query that fetches the 10 most recent published posts, including: author name, tag names, comment count (not the comments themselves). No N+1 queries.
2. Write a migration scenario: you need to add a slug field to Post — unique, non-nullable, but the table already has 10M rows. How do you do this safely without downtime?
3. A query is slow: findMany posts filtered by tag name takes 800ms. Walk through how you diagnose and fix this — show the Prisma query, the raw SQL it generates, and what index you add.
4. When would you drop down from Prisma to raw SQL? Give a real example from this schema.

**A:**
### 1. Fetching 10 Most Recent Published Posts
To fetch the 10 most recent published posts and include author name, tag names, and comment count, we can use the following Prisma query:

```graphql
query {
  posts(limit: 10) {
    title
    content
    author {
      name
      posts {
        title
        content
        tags {
          name
        }
      }
    }
  }
}
```

### 2. Migration Scenario: Adding a Slug Field to Post
If we need to add a slug field to the `Post` model, we can use the following migration:

```graphql
mutation {
  updatePost(slug: "slug", name: "newPostName") {
    id
    title
    content
    tags {
      name
    }
    comments {
      id
      content
      authorId
      author {
        name
      }
    }
    createdAt
  }
}
```

### 3. Diagnosing and Fixing the Query
To diagnose and fix the query where the `Many` relationship is slow, you can add a filter to exclude the `comments` relationship. This way, the query will not load the entire `comments` collection, but only the related `Post` documents:

```graphql
query {
  posts(limit: 10, where: { tags: { $ne: 1 } }) {
    title
    content
    tags {
      name
    }
    comments {
      id
      content
      authorId
      author {
        name
      }
    }
    createdAt
  }
}
```

### 4. Dropping Down from Prisma to Raw SQL
If you need to drop down from Prisma to raw SQL, you can use the `drop` function. This is useful when you want to remove a table structure or alter it without changing the schema.

```sql
-- Drop the table
drop table if exists posts;

-- Create the table
create table posts (
  id int @id @default(autoincrement()),
  title text,
  content text,
  published boolean,
  author_id int,
  author_name text,
  tags text,
  comments (comments) @default(null),
  created_at datetime
);

-- Add a slug field
alter table posts
add column slug text,
update posts
set slug = trim(truncate(replace(post.title, ' ', '_')));

-- Add a new column for comments
alter table posts
add column comments (comments) @default(null),
update posts
set comments = null;

-- Add a new column for tags
alter table posts
add column tags (tags) @default(null),
update posts
set tags = null;

-- Create the Many relationship
alter table posts
add column comments (comments) @default(null),
update posts
set comments = null;

-- Update the schema
-- (This will drop the existing schema and create the new schema)
-- (You can use Prisma's schema tooling or a tool like Flyway or

*Response time: 3.8s*

---

## Question 8
**Q:** You have a full-stack app: React frontend (Vite), Node.js + Express backend, PostgreSQL, Redis.

1. Write a docker-compose.yml for local development with:
   - Hot reload for both frontend and backend
   - PostgreSQL with a named volume (data persists between restarts)
   - Redis
   - Environment variables via .env file
   - Backend waits for PostgreSQL to be healthy before starting (use healthcheck, not depends_on alone)

2. Write a production Dockerfile for the backend (Node.js):
   - Multi-stage build (builder + runtime)
   - Final image runs as non-root user
   - Only production dependencies in final image
   - Image size should be minimized

3. The backend crashes in production (exit code 137). What does this mean and how do you diagnose it?

4. You need to deploy a new version with zero downtime. The database schema changed (additive only — new nullable column). Describe the deployment sequence step by step.

**A:**
Certainly! Below is the detailed solution for your requirements:

### 1. `docker-compose.yml` for Local Development

#### Environment Variables
- `DB_HOST`: PostgreSQL hostname
- `DB_PORT`: PostgreSQL database port
- `DB_USER`: PostgreSQL username
- `DB_PASSWORD`: PostgreSQL password
- `DB_NAME`: PostgreSQL database name

```yaml
version: '3.8'

services:
  db:
    image: postgres:latest
    environment:
      - POSTGRES_DB=db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    image: node:latest
    ports:
      - "5000:5000"
    volumes:
      - db_data:/var/lib/postgresql/data

  frontend:
    build: .
    dependencies:
      - vite
    volumes:
      - frontend_data:/app

  frontend_data:
    depends_on:
      - backend

  db_data:
    depends_on:
      - db

  frontend_data: {{ .Env }}
```

### 2. `docker-compose.yml` for Production

#### Environment Variables
- `DB_HOST`: PostgreSQL hostname
- `DB_PORT`: PostgreSQL database port
- `DB_USER`: PostgreSQL username
- `DB_PASSWORD`: PostgreSQL password
- `DB_NAME`: PostgreSQL database name

```yaml
version: '3.8'

services:
  db:
    image: postgres:latest
    environment:
      - POSTGRES_DB=db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    image: node:latest
    ports:
      - "5000:5000"
    volumes:
      - db_data:/var/lib/postgresql/data

  frontend:
    build: .
    dependencies:
      - vite
    volumes:
      - frontend_data:/app

  frontend_data:
    depends_on:
      - backend

  db_data:
    depends_on:
      - db

  frontend_data: {{ .Env }}
```

### 3. Diagnosing the Backend Crash in Production

When the backend crashes in production, it typically indicates that the database has failed to connect to the PostgreSQL server. To diagnose the issue, follow these steps:

1. **Check the PostgreSQL Logs:**
   - The logs are typically stored in the `/var/log/postgresql/` directory. Look for error messages and stack traces.

2. **Verify Connection Details:**
   - Ensure that the PostgreSQL user and credentials in the `.env` file are correct.
   - Verify that the PostgreSQL port is configured correctly.

3. **Check for Any Errors:**
   - Look for any errors in the logs that might indicate the specific cause of the crash.

### 4. Deployment Sequence Step by Step

#### Step 1: Build the Backend
1. Build the backend Docker image with all necessary dependencies and run the build:
   ```sh
   docker build -t backend .
   ```

#### Step 2: Install Dependencies
1. Install dependencies in the non-root user:
   ```sh
   docker run -d -p 8080:8080 --name backend_0 backend
   ```

#### Step 3: Deploy the Backend
1. Expose the backend port:
   ```sh
   docker run -d -p 5000:5000 backend_0
   ```

#### Step 4: Deploy the Database Schema
1. Update the `.env` file with the new nullable column and add the database data:
   ```env
   DB_HOST=localhost
   DB_PORT=5000
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_NAME=database
   DB_DATA=/app/production_data
   ```

2. Create the database data:
   ```sh
   docker run -d -p 5000:5000 -e DB_DATA=/app/production_data -e DB_NAME=database -e DB_HOST=localhost -e DB_PORT=5000 -e DB_USER=postgres -e DB_PASSWORD=postgres --name db_0 postgres:latest
   ```

3. Add the database data to the .env file:
   ```env
   DB_HOST=localhost
   DB_PORT=5000
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_NAME=database
   DB_DATA=/app/production_data
   ```

4. Start the database service:
   ```sh
   docker run -d -p 5000:5000 -e DB_DATA=/app/production_data -e DB_NAME=database -e DB_HOST=localhost -e DB_PORT=5000 -e DB_USER=postgres -e DB_PASSWORD=postgres --name db_0 postgres:latest
   ```

5. Replace the database data with the new nullable column:
   ```sh
   docker exec -it db_0 cp database data
   docker exec -it db_0 psql -c "ALTER TABLE mytable ADD COLUMN nullable_column TEXT"
   ```

6. Restart the database service:
   ```sh
   docker restart db_0
   ```

#### Step 5: Monitor the Backend and Database
1. Monitor the backend using tools like `kubectl` or the `nginx-ingress` deployment.
2. Use the database monitoring tools (e.g., Prometheus, Grafana, AWS CloudWatch) to ensure the database is healthy.
3. Check the PostgreSQL logs to identify any error messages.

#### Step 6: Ensure Zero-Downtime Deployment
1. Deploy the new version of the application with a zero-downtime deployment strategy:
   - Update the database schema.
   - Replace the database data with the new nullable column.
   - Deploy the updated database.

2. Use tools like `cron` or `systemd` to schedule the deployment.

### Conclusion

By following these steps, you can effectively manage and deploy a new version of your application with minimal downtime. Monitor the logs, check the database, and use monitoring tools to ensure the new version is running smoothly.

*Response time: 7.5s*

---

## Question 9
**Q:** You are building a collaborative document editor (like Google Docs, simplified):
- Multiple users can edit the same document simultaneously
- Each user sees others' cursors in realtime
- Changes are broadcast to all connected clients
- If a user disconnects and reconnects, they get the latest document state

Implement the server side in Node.js using the ws library:
1. Connection handling — how do you associate a WebSocket connection with a user and document?
2. Message protocol — define the message types (JSON) for: join document, text change, cursor move, user left
3. Broadcasting — when user A makes a change, how do you send it to all other users in the same document but NOT back to user A?
4. Reconnection — how do you handle a user rejoining after disconnect?
5. What happens if two users edit the exact same position simultaneously? You don't need to implement OT/CRDT — just explain the problem and name the solution approaches.

Write the core server implementation (connection map, message routing, broadcast logic).

**A:**
To implement a collaborative document editor using Node.js with the ws library, we'll need to define the server-side connections, message routing, broadcasting, and handling user reconnections. Below is a basic implementation of the server-side code for a simple collaborative document editor.

### 1. Connection Handling

We need a connection map to associate a WebSocket connection with a user and document. This is typically done using a hash table where each key is a user and the value is a WebSocket connection.

```javascript
const WebSocket = require('ws');

const wsMap = {};

const connectUser = (user, docId) => {
  if (!wsMap[user]) wsMap[user] = new WebSocket(`ws://localhost:${docId}`);
  wsMap[user].onopen = () => console.log(`User ${user} connected to document ${docId}`);
  wsMap[user].onclose = () => console.log(`User ${user} disconnected from document ${docId}`);
  wsMap[user].onmessage = (message) => console.log(`User ${user} sent message: ${message.data}`);
  wsMap[user].onclose = () => console.log(`User ${user} closed the connection`);
};

const disconnectUser = (user) => {
  delete wsMap[user];
};

const getUserMap = () => {
  return Object.fromEntries(Object.entries(wsMap).map(([user, ws]) => [user, ws]));
};
```

### 2. Message Protocol

Define the message types and their associated functions:

```javascript
const types = {
  'JOIN': joinDocument,
  'TEXT': changeDocument,
  'MOVE': cursorMove,
  'LEFT': userLeft,
};

const joinDocument = (userId) => {
  return async (documentId) => {
    const ws = wsMap[userId];
    if (ws) {
      await ws.send(JSON.stringify({ type: 'JOIN', userId, docId }));
      await ws.send(JSON.stringify({ type: 'JOIN', userId, docId }));
      await ws.send(JSON.stringify({ type: 'JOIN', userId, docId }));
    }
  };
};

const changeDocument = (userId, docId) => {
  return async (data) => {
    const ws = wsMap[userId];
    if (ws) {
      await ws.send(JSON.stringify({ type: 'TEXT', docId, ...data }));
      await ws.send(JSON.stringify({ type: 'TEXT', docId, ...data }));
    }
  };
};

const cursorMove = (userId, docId) => {
  return async (data) => {
    const ws = wsMap[userId];
    if (ws) {
      await ws.send(JSON.stringify({ type: 'MOVE', docId, ...data }));
    }
  };
};

const userLeft = (userId) => {
  return async (docId) => {
    await wsMap[userId].close();
  };
};
```

### 3. Broadcasting

When a user joins a document, a broadcast message should be sent to all connected clients in the document.

```javascript
const sendBroadcast = (userId, docId) => {
  const ws = wsMap[userId];
  if (ws) {
    ws.send(JSON.stringify({ type: 'JOIN', docId }));
  }
};
```

### 4. Reconnection

When a user rejoins the same document, the current connection is closed, and a new connection is made.

```javascript
const reconnect = (userId, docId) => {
  const ws = wsMap[userId];
  if (ws) {
    ws.close();
    wsMap[userId] = new WebSocket(`ws://localhost:${docId}`);
    wsMap[userId].onopen = () => sendBroadcast(userId, docId);
  }
};
```

### 5. Handling User Reconnections

If two users edit the exact same position simultaneously, they will be disconnected and reconnected separately. This is handled by:

- Sending a `LEFT` message to all other users in the document.
- Reinitializing the document in the other user's document and sending a `JOIN` message to the other user.

```javascript
const sendReconnection = (userId, docId) => {
  const ws = wsMap[userId];
  if (ws) {
    ws.send(JSON.stringify({ type: 'LEFT', docId }));
    wsMap[userId] = new WebSocket(`ws://localhost:${docId}`);
    wsMap[userId].onopen = () => sendBroadcast(userId, docId);
  }
};

const reconnectUser = (userId, docId) => {
  const ws = wsMap[userId];
  if (ws) {
    ws.send(JSON.stringify({ type: 'LEFT', docId }));
    wsMap[userId] = new WebSocket(`ws://localhost:${docId}`);
    wsMap[userId].onopen = () => sendBroadcast(userId, docId);
  }
};

const reconnectUser2 = (userId, docId) => {
  const ws = wsMap[userId];
  if (ws) {
    ws.send(JSON.stringify({ type: 'LEFT', docId }));
    wsMap[userId] = new WebSocket(`ws://localhost:${docId}`);
    wsMap[userId].onopen = () => sendBroadcast(userId, docId);
  }
};
```

### 6. Handling Collisions

When a user disconnects and rejoins the document, the current connection is closed, and a new connection is made:

```javascript
disconnectUser(userId);
disconnectUser(docId);
```

### 7. Example Usage

To use this server-side implementation, you would typically run the server and then use the WebSocket client to interact with the server. Here's a brief example using Node.js:

```javascript
const { WebSocket } = require('ws');
const ws = new WebSocket('ws://localhost:8080');

const map = getUserMap();
const wsMap = map;
```

This setup provides a basic implementation of a collaborative document editor using Node.js with the ws library. You can further enhance the implementation based on your specific requirements.

*Response time: 7.2s*

---

## Question 10
**Q:** You are building a GraphQL API for a recipe platform. A recipe has: title, ingredients (each with name, amount, unit), steps, author, tags, ratings (each with score and comment).

1. Write the complete GraphQL schema (SDL) for this domain
2. Write resolvers for:
   - Query.recipes(filter: {tag: String, minRating: Float}, pagination: {page: Int, limit: Int})
   - Mutation.addRating(recipeId: ID!, score: Float!, comment: String)
   - The Recipe.averageRating computed field
3. The recipes query causes N+1 problem when fetching authors. Show the problem with a concrete example, then fix it using DataLoader.
4. A client wants to fetch recipe title + author name + first 3 ingredients in one request. Show the exact GraphQL query they would write.
5. When would you choose GraphQL over REST? When would you NOT?

**A:**
### 1. Complete GraphQL Schema (SDL) for the Recipe Platform

The complete GraphQL schema for the recipe platform would include several types such as `Recipe`, `RecipeIngredient`, `RecipeStep`, `RecipeAuthor`, `Rating`, and `RecipeRating`. Here is the schema in the form of an SSDL:

```json
{
  "type": "recipe",
  "fields": [
    {
      "name": "title",
      "type": "string"
    },
    {
      "name": "author",
      "type": "string",
      "description": "The name of the author"
    },
    {
      "name": "tags",
      "type": "array",
      "description": "The tags associated with the recipe"
    },
    {
      "name": "ingredients",
      "type": "array",
      "description": "An array of {name: string, amount: number, unit: string} for each ingredient"
    },
    {
      "name": "steps",
      "type": "array",
      "description": "An array of {step: string, score: number, comment: string} for each step"
    },
    {
      "name": "ratings",
      "type": "array",
      "description": "An array of {score: number, comment: string} for each rating"
    },
    {
      "name": "author_id",
      "type": "integer",
      "description": "The ID of the author"
    },
    {
      "name": "author_name",
      "type": "string",
      "description": "The name of the author"
    },
    {
      "name": "ratings_id",
      "type": "integer",
      "description": "The ID of the rating"
    },
    {
      "name": "author_rating",
      "type": "number",
      "description": "The rating for the author"
    },
    {
      "name": "ingredients_id",
      "type": "integer",
      "description": "The ID of each ingredient"
    },
    {
      "name": "ratings_count",
      "type": "number",
      "description": "The number of ratings the recipe has"
    },
    {
      "name": "recipes",
      "type": "array",
      "description": "An array of {title: string, ingredients: {name: string, amount: number, unit: string}, steps: {step: string, score: number, comment: string}, author_id: integer, author_name: string, ratings: {id: string, score: number, comment: string}, author_rating: number, ingredients_id: integer, ratings_count: number, tags: array, tags_count: number, tags_id: integer, rating: number, rating_count: number, rating_id: integer, author_rating_id: integer, ratings_count: number}"}
  ],
  "required": ["title", "author", "tags"],
  "relationships": {
    "author": {
      "type": "author",
      "relationships": {
        "ingredients": {
          "type": "ingredient",
          "relationships": {
            "amount": {
              "type": "number",
              "description": "The amount of the ingredient"
            },
            "unit": {
              "type": "string",
              "description": "The unit of the ingredient"
            }
          }
        }
      }
    },
    "ratings": {
      "type": "rating",
      "relationships": {
        "author": {
          "type": "author",
          "relationships": {
            "rating": {
              "type": "rating",
              "relationships": {
                "id": {
                  "type": "integer",
                  "description": "The rating ID"
                }
              }
            }
          }
        }
      }
    }
  },
  "non-nullable": {
    "author_id": {
      "type": "integer",
      "description": "The ID of the author"
    },
    "author_name": {
      "type": "string",
      "description": "The name of the author"
    },
    "author_rating": {
      "type": "number",
      "description": "The rating for the author"
    },
    "ingredients_id": {
      "type": "integer",
      "description": "The ID of each ingredient"
    },
    "ratings_count": {
      "type": "number",
      "description": "The number of ratings the recipe has"
    },
    "tags_id": {
      "type": "integer",
      "description": "The ID of the tags"
    },
    "tags_count": {
      "type": "number",
      "description": "The number of tags associated with the recipe"
  }
}
}
```

### 2. Resolver for Query.recsions(filter: {tag: String, minRating: Float}, pagination: {page: Int, limit: Int})
The resolver for the `recipes` query causes a N+1 problem. Here is how you can handle this:

```graphql
{
  recipes(filter: {tag: "string", minRating: Float}, pagination: {page: Int, limit: Int})
}
```

### 3. Problem with the Recipes Query
The problem with the `recipes` query is that it fetches all the recipes with the given `tag` and `minRating`, even if a user might have added more than one recipe with the same `tag` and `minRating`. For example, if a user has added more than one recipe with the same `tag` and `minRating`, the `recipes` query will fetch all of those recipes.

### 4. Query to Fetch Recipe Title + Author Name + First 3 Ingredients
To fetch the recipe title, author name, and first 3 ingredients in one request, you can use the following query:

```graphql
{
  recipe {
    title
    authorName
    first3Ingredients {
      ingredients
      score
      comment
    }
  }
}
```

### 5. GraphQL vs. REST
- **GraphQL**: GraphQL is an endpoint-oriented architecture that allows for more flexible and scalable APIs. It is designed to handle complex queries and updates without the need for client-side JavaScript. It supports a wide range of data sources, such as databases, NoSQL, and external APIs. The data is stored in a schema that the client can interact with, making it easier to query and update the data.
- **REST**: REST (Representational State Transfer) is a technique that provides a simpler client-server architecture. It uses HTTP methods such as GET, POST, PUT, and DELETE to interact with the server. While REST can be useful for client-side applications, it does not provide the same level of flexibility and scalability that GraphQL offers.

### Choosing GraphQL vs. REST
- **GraphQL**: It is better suited for applications that handle large amounts of data and require complex queries and updates. It is well-suited for applications that need to handle a high volume of data and transactions.
- **REST**: It is better suited for applications that need to handle simple, small updates and simple queries. REST is less powerful and flexible than GraphQL, and it is less appropriate for applications that handle a large amount of data and complex queries.

### Conclusion
In summary, the choice between GraphQL and REST depends on the specific needs of the application. For applications that handle large amounts of data and complex queries, GraphQL is the better choice. For applications that need to handle simple, small updates and simple queries, REST is the better choice.

*Response time: 9.0s*

---

## Question 11
**Q:** Implement the following UI layout using only CSS (no JavaScript, no CSS frameworks):

┌─────────────────────────────────────────┐
│  HEADER (fixed, full width, 60px tall)  │
├──────────┬──────────────────────────────┤
│          │                              │
│ SIDEBAR  │      MAIN CONTENT            │
│ (240px,  │  (fills remaining space,     │
│ scrolls  │   scrolls independently)     │
│ indepen- │                              │
│ dently)  │  ┌────────┐ ┌────────┐      │
│          │  │ CARD   │ │ CARD   │      │
│          │  └────────┘ └────────┘      │
│          │  ┌────────┐ ┌────────┐      │
│          │  │ CARD   │ │ CARD   │      │
│          │  └────────┘ └────────┘      │
│          │  (cards: responsive grid,    │
│          │   2 cols ≥768px, 1 col <768) │
└──────────┴──────────────────────────────┘

Requirements:
1. Header is fixed — content does not scroll behind it
2. Sidebar and main content fill the full viewport height below the header
3. Sidebar and main scroll independently
4. Cards use CSS Grid — 2 columns on desktop, 1 column on mobile (≤768px)
5. Each card has: image (16:9 ratio, always maintained), title, description, footer with two buttons (one left-aligned, one right-aligned)
6. No JavaScript. No frameworks. Valid HTML + CSS only.

Write the complete HTML + CSS. Explain your layout approach (Flexbox vs Grid choices).

**A:**
Certainly! Let's break down the layout using both Flexbox and Grid, and explain the approach:

### 1. HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UI Layout Example</title>
    <style>
        /* Reset some common styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background-color: #f4f4f4;
        }

        /* Fix header width and spacing */
        .header {
            width: 100%;
            height: 60px;
            position: fixed;
            top: 0;
        }

        /* Sidebar and main content */
        .sidebar {
            display: flex;
            flex-direction: column;
            height: 100%;
        }

        .main-content {
            flex-grow: 1;
            flex: 0 0 auto;
            overflow-y: auto;
            height: 100%;
        }

        /* Responsive card cards */
        .card {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }

        .card img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .card .card-title {
            margin-bottom: 10px;
            font-size: 1.5em;
            color: #333;
        }

        .card .card-description {
            font-size: 1.2em;
            color: #666;
        }

        .card .card-footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 20px;
        }

        .card .card-footer button {
            margin: 0 10px;
            display: block;
            margin-bottom: 5px;
            padding: 10px 20px;
            border: none;
            background: none;
            color: #000;
            cursor: pointer;
        }

        .card .card-footer button.left-aligned {
            align-self: flex-end;
        }

        .card .card-footer button.right-aligned {
            align-self: flex-start;
        }

        /* Responsive Grid layout */
        .grid-container {
            width: 100%;
            height: 100%;
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 20px;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <!-- Header content stays fixed -->
    </div>
    <div class="sidebar">
        <div class="main-content">
            <div class="card">
                <img src="card-image" alt="Card Title">
                <div class="card-title">Card Title</div>
                <div class="card-description">Card Description</div>
                <div class="card-footer">
                    <button class="left-aligned">Left-aligned</button>
                    <button class="right-aligned">Right-aligned</button>
                </div>
            </div>
        </div>
        <div class="card">
            <img src="card-image" alt="Card Title">
            <div class="card-title">Card Title</div>
            <div class="card-description">Card Description</div>
            <div class="card-footer">
                <button class="left-aligned">Left-aligned</button>
                <button class="right-aligned">Right-aligned</button>
            </div>
        </div>
    </div>
    <div class="footer">
        <!-- Footer content scrolls independently -->
    </div>
</body>
</html>
```

### 2. Flexbox Layout Approach

To achieve a similar layout using Flexbox, we can use the following code:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UI Layout Example</title>
    <style>
        /* Reset some common styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background-color: #f4f4f4;
        }

        /* Fix header width and spacing */
        .header {
            width: 100%;
            height: 60px;
            position: fixed;
            top: 0;
        }

        /* Sidebar and main content */
        .sidebar {
            display: flex;
            flex-direction: column;
            height: 100%;
        }

        .main-content {
            flex: 0 0 auto;
            overflow-y: auto;
            height: 100%;
        }

        /* Responsive card cards */
        .card {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }

        .card img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .card .card-title {
            margin-bottom: 10px;
            font-size: 1.5em;
            color: #333;
        }

        .card .card-description {
            font-size: 1.2em;
            color: #666;
        }

        .card .card-footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 20px;
        }

        .card .card-footer button {
            margin: 0 10px;
            display: block;
            margin-bottom: 5px;
            padding: 10px 20px;
            border: none;
            background: none;
            color: #000;
            cursor: pointer;
        }

        .card .card-footer button.left-aligned {
            align-self: flex-end;
        }

        .card .card-footer button.right-aligned {
            align-self: flex-start;
        }

        /* Responsive Grid layout */
        .grid-container {
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 20px;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <!-- Header content stays fixed -->
    </div>
    <div class="sidebar">
        <div class="main-content">
            <div class="card">
                <img src="card-image" alt="Card Title">
                <div class="card-title">Card Title</div>
                <div class="card-description">Card Description</div>
                <div class="card-footer">
                    <button class="left-aligned">Left-aligned</button>
                    <button class="right-aligned">Right-aligned</button>
                </div>
            </div>
            <div class="card">
                <img src="card-image" alt="Card Title">
                <div class="card-title">Card Title</div>
                <div class="card-description">Card Description</div>
                <div class="card-footer">
                    <button class="left-aligned">Left-aligned</button>
                    <button class="right-aligned">Right-aligned</button>
                </div>
            </div>
        </div>
        <div class="card">
            <img src="card-image" alt="Card Title">
            <div class="card-title">Card Title</div>
            <div class="card-description">Card Description</div>
            <div class="card-footer">
                <button class="left-aligned">Left-aligned</button>
                <button class="right-aligned">Right-aligned</button>
            </div>
        </div>
    </div>
    <div class="footer">
        <!-- Footer content scrolls independently -->
    </div>
</body>
</html>
```

### Explanation:

#### Flexbox Layout:

- **Flexbox**: We used Flexbox to arrange the card items within the `.card` containers. This ensures that cards are positioned side by side (responsive).
- **Flex Direction**: `.main-content` uses Flex-direction: column; to arrange the cards side by side.
- **Grid Layout**: `.grid-container` uses Flexbox to arrange the cards in a grid-like layout with two columns, each covering the remaining space.
- **Gap and Padding**: Padding and gap values ensure that the card content does not overlap or scroll behind the header.

#### Grid Layout:

- **Grid Templates**: Each card uses a grid template with 1 column and 1 row.
- **Grid Rows**: Grid rows are defined with 1 column and 1 row.
- **Grid Columns**: Each card uses a grid column with 1 column and 1 row.
- **Gap and Padding**: Padding and gap values ensure that the card content does not overlap or scroll behind the header.

Both layouts achieve the same visual effect, but the Flexbox approach provides more control and flexibility for content placement. The Grid approach is simpler but may not be as effective for certain use cases, such as dynamic content or responsive design.

*Response time: 11.5s*

---

## Question 12
**Q:** You are asked to add real-time notifications to the existing project management tool. Users should be notified when: a task is assigned to them, a comment is added to their task, a deadline is approaching (within 24h).

Design the notification system:
1. What transport mechanism would you use and why? (WebSocket, SSE, polling, push notifications — compare and justify)
2. How do you store notifications? Design the database schema.
3. How do you handle a user who is offline — do they get missed notifications when they come back online?
4. The deadline check needs to run every hour for all tasks. How do you implement this? (cron job, queue, event-driven?) — show the implementation approach.
5. How do you scale this if there are 100,000 concurrent users?

**A:**
1. **Transport Mechanism:** WebSocket (WebSocket) is a suitable choice for real-time notifications since it allows real-time communication between the client and server. WebSocket provides a reliable and fast communication channel, making it ideal for real-time data exchange, including notifications. **Reasons for using WebSocket:**
   - **High Performance:** WebSocket ensures that the communication is both efficient and uninterrupted. It allows the client to send and receive data without interruptions.
   - **Transparency:** By using WebSocket, users can see the changes made to their notifications in real-time, unlike some other technologies like SSE (Server-Sent Events) that require waiting for the server to send the data before it can be seen.
   - **Streamed Data:** WebSocket data is streamed in real-time, so notifications can be accessed and handled instantly, even if the server is down or offline.

2. **Database Schema:**
   - **Task:** A database table to store information about tasks. Each task would have fields like `task_id`, `user_id`, `assigned_to`, `status`, `deadline`, and `comments`.
   - **User:** A separate table for storing user information. Each user would have a unique `user_id` and fields like `username`, `name`, `email`, `address`, and `last_seen`.
   - **Notifications:** A table to store notifications. Each notification would have fields like `notification_id`, `user_id`, `task_id`, `action`, and `timestamp`.

3. **Handling Offline Users:**
   - **Offline Users:** When a user is offline, they can get notifications by using a user agent that identifies them as an offline user. The user agent can be a combination of their username, email, or a unique identifier.

4. **Deadline Check:**
   - **cron job:** You can implement the deadline check as a cron job that runs every hour, ensuring that the deadline is checked at the same time every hour.
   - **Queue:** Another approach is to use a queue system, where tasks are placed in a queue and processed in a queue-based manner. When a task is added, it goes to the queue and the next available user is notified.

5. **Scaling:**
   - **Database Size:** If the database is very large, you can optimize by storing user data, task data, and notifications in a way that minimizes redundancy and ensures the database remains lightweight.
   - **User Load:** To scale, you can add more users to the system, but this might introduce new issues like increased network usage and database capacity.
   - **Notifications:** If there are a large number of users, adding more notifications per user might not be practical. You might consider a hybrid approach where users are notified based on their activity or time.
   - **Database Size:** If the database is too large, you can limit the number of notifications a user can receive by setting a limit on the number of notifications that can be sent per user.

Here is the code snippet for a simplified version of how a user might interact with the system:

```python
import asyncio
from queue import Queue
from threading import Thread

# Define the database schema
tasks = {
    '12345': {'user_id': 1, 'task_id': 1, 'assigned_to': 'user1', 'status': 'new', 'deadline': '2023-06-15 10:00', 'comments': 'Task 1'},
    '67890': {'user_id': 2, 'task_id': 2, 'assigned_to': 'user2', 'status': 'new', 'deadline': '2023-06-15 11:00', 'comments': 'Task 2'},
    # Add more users and tasks...
}

users = {
    'user1': {'user_id': 1, 'name': 'User 1', 'email': 'user1@example.com'},
    'user2': {'user_id': 2, 'name': 'User 2', 'email': 'user2@example.com'}
}

# Task class
class Task:
    def __init__(self, user_id, task_id, assigned_to, status, deadline, comments):
        self.user_id = user_id
        self.task_id = task_id
        self.assigned_to = assigned_to
        self.status = status
        self.deadline = deadline
        self.comments = comments

# Notification class
class Notification:
    def __init__(self, user_id, task_id, action, timestamp):
        self.user_id = user_id
        self.task_id = task_id
        self.action = action
        self.timestamp = timestamp

# User activity
def user_activity(user_id, activity):
    # Add user activity to the database
    tasks[user_id]['activity'] = activity
    # Send notifications to other users
    for other_user in users:
        if other_user != user_id:
            users[other_user]['activity'] += activity
            tasks[other_user]['task'] += activity

# Main loop to handle notifications
def main():
    # Initialize database connections
    tasks_db = Queue()
    notifications_db = Queue()

    # Initialize user activity
    user_activity(1, 'active')

    # Handle user activity
    user_thread = Thread(target=user_activity, args=(1,))
    user_thread.start()

    # Main loop to handle notifications
    while True:
        task = tasks_db.get()  # Get the next task from the database
        if task is None:
            break
        if task['user_id'] != 1:
            continue
        if task['status'] == 'active':
            notifications_db.put(Notification(user1, 1, 'active', time.time()))
        else:
            notifications_db.put(Notification(user2, 1, 'inactive', time.time()))

        # Get new notifications
        tasks_db.put(task['task'])
        notifications_db.put(task['user_id'])
        tasks_db.put(task['task_id'])
        tasks_db.put(task['user_id'])
        tasks_db.put(task['deadline'])
        tasks_db.put(task['comments'])

        # Schedule the next user activity
        user_activity(user2, 'active')

if __name__ == '__main__':
    asyncio.run(main())
```

In this design, the user's activity is tracked in the database and the notifications are sent to the user's inbox. The user's activity is handled by a separate thread, and the system is updated in real-time as tasks are added, changed, or removed.

*Response time: 7.7s*

---
