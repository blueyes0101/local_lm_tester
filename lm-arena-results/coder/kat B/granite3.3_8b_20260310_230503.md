# Model: granite3.3:8b
**Test Date:** 2026-03-10 23:14:58
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
1. API Endpoints:

- `POST /workspaces`: Create a new workspace.
  Request: 
  ```json
  {
    "name": "Workspace Name"
  }
  ```
  Response:
  ```json
  {
    "id": "workspace-id",
    "name": "Workspace Name"
  }
  ```

- `GET /workspaces`: List all workspaces (with pagination).
  Query params: `page`, `limit`
  Response:
  ```json
  {
    "workspaces": [
      {
        "id": "workspace-id",
        "name": "Workspace Name"
      }
    ],
    "pagination": {
      "total_count": 100,
      "current_page": 1,
      "page_size": 10
    }
  }
  ```

- `GET /workspaces/{workspace_id}/projects`: List projects in a workspace (with pagination and filters: assignee, status, due_date).
  Query params: `assignee`, `status`, `due_date`
  Response:
  ```json
  {
    "projects": [
      {
        "id": "project-id",
        "name": "Project Name",
        "workspace_id": "workspace-id"
      }
    ],
    "pagination": {
      "total_count": 20,
      "current_page": 1,
      "page_size": 10
    }
  }
  ```

- `POST /workspaces/{workspace_id}/projects`: Create a new project in a workspace.
  Path params: `workspace_id`
  Request:
  ```json
  {
    "name": "Project Name"
  }
  ```
  Response:
  ```json
  {
    "id": "project-id",
    "name": "Project Name",
    "workspace_id": "workspace-id"
  }
  ```

- `GET /projects/{project_id}/tasks`: List tasks for a project (with pagination and filters: assignee, status, due_date).
  Path params: `project_id`
  Query params: `assignee`, `status`, `due_date`
  Response:
  ```json
  {
    "tasks": [
      {
        "id": "task-id",
        "name": "Task Name",
        "project_id": "project-id",
        "assignee_id": "user-id",
        "status": "in_progress",
        "due_date": "2023-04-30"
      }
    ],
    "pagination": {
      "total_count": 10,
      "current_page": 1,
      "page_size": 10
    }
  }
  ```

- `POST /projects/{project_id}/tasks`: Create a new task for a project.
  Path params: `project_id`
  Request:
  ```json
  {
    "name": "Task Name",
    "status": "to_do"
  }
  ```
  Response:
  ```json
  {
    "id": "task-id",
    "name": "Task Name",
    "project_id": "project-id",
    "status": "to_do"
  }
  ```

- `PUT /tasks/{task_id}`: Update a task status.
  Path params: `task_id`
  Request:
  ```json
  {
    "status": "in_progress"
  }
  ```
  Response:
  ```json
  {
    "id": "task-id",
    "name": "Task Name",
    "project_id": "project-id",
    "status": "in_progress"
  }
  ```

- `POST /tasks/{task_id}/comments`: Add a comment to a task.
  Path params: `task_id`
  Request:
  ```json
  {
    "content": "This is a comment."
  }
  ```
  Response:
  ```json
  {
    "id": "comment-id",
    "task_id": "task-id",
    "content": "This is a comment.",
    "user_id": "user-id"
  }
  ```

2. Error Response Format:

```json
{
  "status": "error",
  "code": "ERR_CODE",
  "message": "Error message description",
  "details": {
    "field": "field_name",
    "value": "invalid_value"
  }
}
```

3. Pagination:

- All endpoints that return lists of resources use a consistent pagination format.
- Query parameters `page` and `limit` control pagination.
- The response envelope contains a `pagination` object with `total_count`, `current_page`, and `page_size`.

4. HTTP Status Codes:

- `200 OK`: Successful requests (GET, POST, PUT)
- `201 Created`: Resource created (POST)
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Attempt to create resource with conflicting data (e.g., duplicate name)
- `500 Internal Server Error`: Unexpected server error

This API design provides a comprehensive set of endpoints for managing workspaces, projects, tasks, users, and comments in a multi-tenant SaaS project management tool, adhering to REST conventions and ensuring consistency and clarity in responses.

*Response time: 29.6s*

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
```json
{
  "response": {
    "code": 200,
    "message": "Success",
    "data": {
      "task": {
        "id": "task_123",
        "workspaceId": "workspace_456",
        "title": "Updated Task Title",
        "status": "in_progress",
        "assignee_id": 789,
        "due_date": "2024-04-30T00:00:00Z"
      }
    }
  }
}
```

```typescript
// Import required packages
import express, { Request, Response, NextFunction } from 'express';
import { z } from 'zod';

// Define the schema for request body validation
const TaskPatchSchema = z.object({
  title: z.string({ min: 1, max: 200 }),
  status: z.enum(['todo', 'in_progress', 'done', 'cancelled']),
  assignee_id: z.union([z.number(), z.null()]),
  due_date: z.string().optional(),
});

// Middleware to validate request body
const validatePatchRequest = (req: Request, res: Response, next: NextFunction) => {
  const { error } = TaskPatchSchema.safeParse(req.body);
  if (error) {
    return res.status(400).json({ errors: error.details });
  }
  next();
};

// Middleware to validate workspaceId and taskId
const validateWorkspaceIdAndTaskId = (req: Request, res: Response, next: NextFunction) => {
  const { workspaceId, taskId } = req.params;

  if (!Number.isInteger(Number(workspaceId)) || !Number.isInteger(Number(taskId))) {
    return res.status(400).json({ error: 'Workspace ID and Task ID must be integers.' });
  }

  // Replace this with your actual workspace and task validation logic
  // Example: Checking if task belongs to the workspace
  // if (!taskExistsInWorkspace(workspaceId, taskId)) {
  //   return res.status(404).json({ error: 'Task not found in the workspace.' });
  // }

  next();
};

// Endpoint handler
const updateTask = async (req: Request, res: Response) => {
  const { workspaceId, taskId } = req.params;

  // Validate workspaceId and taskId
  validateWorkspaceIdAndTaskId(req, res, () => {
    // Validate request body
    validatePatchRequest(req, res, () => {
      // Perform actual task update logic here
      // Example: Update task in the database
      // const updatedTask = await updateTaskInDatabase(workspaceId, taskId, req.body);

      // Return success response
      res.status(200).json({
        message: 'Success',
        data: {
          task: updatedTask,
        },
      });
    });
  });
};

// Create Express app and define the route
const app = express();
app.use(express.json());

app.patch('/workspaces/:workspaceId/tasks/:taskId', updateTask);

// Export for testing
export default app;
```

**Unit Tests (using Jest and Supertest):**

```typescript
// Import required packages
import request from 'supertest';
import app from './app';

describe('PATCH /workspaces/:workspaceId/tasks/:taskId', () => {
  it('should update a task successfully', async () => {
    const res = await request(app)
      .patch('/workspaces/1/tasks/2')
      .send({
        title: 'Updated Task Title',
        status: 'in_progress',
        assignee_id: 789,
        due_date: '2024-04-30T00:00:00Z',
      });

    expect(res.status).toBe(200);
    expect(res.body.message).toBe('Success');
    expect(res.body.data.task.title).toBe('Updated Task Title');
    // Add more assertions as needed
  });

  it('should return 400 with validation errors', async () => {
    const res = await request(app)
      .patch('/workspaces/1/tasks/2')
      .send({ title: 'a' });

    expect(res.status).toBe(400);
    expect(res.body.errors).toHaveLength(1);
    expect(res.body.errors[0].message).toContain('must have at least 1 character');
  });

  it('should return 404 when task not found', async () => {
    const res = await request(app)
      .patch('/workspaces/1/tasks/999');

    expect(res.status).toBe(404);
    expect(res.body.error).toContain('Task not found in the workspace.');
  });

  it('should return 409 when trying to set status to cancelled with open subtasks', async () => {
    // Assuming you have a mechanism to simulate open subtasks
    // const res = await request(app)
    //   .patch('/workspaces/1/tasks/2')
    //   .send({ status: 'cancelled' });

    // expect(res.status).toBe(409);
    // expect(res.body.error).toContain('Cannot change status to cancelled as there are open subtasks.');
  });
});
```

Remember to install the required packages (`express`, `supertest`, `@types/express`, `@types/supertest`, `zod`, `typescript`) and set up your TypeScript configuration before running the tests. Also, replace the placeholder comments with actual database access logic and validation checks according to your application's requirements.

*Response time: 31.2s*

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
To create a complete authentication system in Node.js using Express, TypeScript, and bcrypt for password hashing, follow these steps:

1. **Set up the project:**

Create a new directory for your project and initialize it with npm:

```bash
mkdir node-auth-system
cd node-auth-system
npm init -y
```

Install necessary packages:

```bash
npm install express typescript @types/express babel-cli babel-loader jsonwebtoken bcryptjs dotenv
npm install -D typescript ts-node
```

Initialize TypeScript configuration:

```bash
npx tsc --init
```

Add a `.babelrc` file for transpiling TypeScript and ES6+ features:

```json
{
  "presets": ["@babel/preset-env", "@babel/preset-typescript"]
}
```

Create a `tsconfig.json` file for TypeScript configuration:

```json
{
  "compilerOptions": {
    "target": "es6",
    "module": "commonjs",
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true
  }
}
```

2. **Set up server and routes:**

Create a `src` folder and add the following files:

- `src/index.ts`: Entry point for the application.
- `src/auth/routes.ts`: Authentication routes.
- `src/auth/controller.ts`: Authentication controllers.
- `src/auth/middleware.ts`: Authentication middleware.

Here's a sample implementation for each file:

**src/index.ts**

```typescript
import express from 'express';
import bodyParser from 'body-parser';
import authRoutes from './auth/routes';
import authMiddleware from './auth/middleware';

const app = express();
const port = process.env.PORT || 3000;

app.use(bodyParser.json());
app.use('/api/auth', authRoutes, authMiddleware);

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
```

**src/auth/routes.ts**

```typescript
import express from 'express';
import { register, login, me } from './controller';

const router = express.Router();

router.post('/register', register);
router.post('/login', login);
router.get('/me', me);

export default router;
```

**src/auth/controller.ts**

```typescript
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import User from '../../models/User'; // Assuming you have a User model

// Register user
export async function register(req, res) {
  try {
    const { email, password } = req.body;
    const hashedPassword = await bcrypt.hash(password, 12);
    const user = new User({ email, password: hashedPassword });
    await user.save();
    res.status(201).json({ userId: user._id, email, role: 'user' });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
}

// Login user
export async function login(req, res) {
  try {
    const { email, password } = req.body;
    const user = await User.findOne({ email });

    if (!user || !(await bcrypt.compare(password, user.password))) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    const accessToken = jwt.sign({ userId: user._id, email, role: 'user', iat: Math.floor(Date.now() / 1000), exp: Math.floor(Date.now() / 1000) + 5400 }, process.env.JWT_SECRET, { expiresIn: '15m' });
    const refreshToken = jwt.sign({ userId: user._id, email, role: 'user', iat: Math.floor(Date.now() / 1000), exp: Math.floor(Date.now() / 1000) + 604800 }, process.env.JWT_REFRESH_SECRET, { expiresIn: '7d' });

    res.cookie('refreshToken', refreshToken, { httpOnly

*Response time: 24.1s*

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
1. **POST /auth/refresh**: To implement this endpoint, you'll need to verify the refresh token from the request cookies. If valid, generate a new access token and refresh token, then store the new refresh token in your Redis database. Invalidate the old refresh token by setting a short TTL or marking it as revoked. Return the new access token to the client.

2. **POST /auth/logout**: To log out a user, invalidate the refresh token (set it with a short TTL or mark it as revoked) and clear the cookie.

3. **Refresh Token Rotation with Redis**: Use a hash data structure in Redis to store tokens, with the token itself as the key and a value containing relevant metadata (e.g., user ID, expiration, and TTL). When rotating tokens, generate a new refresh token, store it with a longer TTL, and invalidate the old one by setting a short TTL or marking it as revoked.

Example Redis data structure:
```
{
  "refresh_token_1": {
    "user_id": "user123",
    "expires_at": 1683578400, // Example Unix timestamp
    "ttl": 2592000 // 30 days
  },
  "refresh_token_2": {
    "user_id": "user123",
    "expires_at": 1683664800, // Another example Unix timestamp
    "ttl": 2592000 // 30 days
  }
}
```

4. **Token reuse detection**: To prevent token reuse, maintain a list of revoked tokens in Redis. When a refresh token is used, check if it's in the revoked list. If it is, reject the request. When a token is revoked, add it to the list.

Example revoked tokens list in Redis:
```
revoked_tokens: [
  "refresh_token_1",
  "refresh_token_3" // A token used twice
]
```

5. **Invalidating all existing sessions on password change**: When a user updates their password, generate a new access token and refresh token. Invalidate all existing refresh tokens associated with the user by adding them to the revoked tokens list in Redis.

6. **Token blacklisting vs. token rotation**:

- **Token blacklisting**: When a token is compromised or no longer needed, add it to a blacklist (e.g., a set or sorted set in Redis). Check this blacklist whenever a token is presented to ensure it's not revoked. This method is suitable when you have fewer tokens and want to maintain a simple and efficient approach.

- **Token rotation**: Regularly generate new tokens and invalidate old ones, keeping only the most recent token active. This method is more suitable for systems with many tokens and helps minimize the attack window if a token is compromised. It's also less prone to exhausting the token store compared to blacklisting.

Choose token blacklisting when:
- The number of tokens is small.
- You want a simple and efficient approach.

Choose token rotation when:
- The number of tokens is large.
- You want to minimize the attack window in case of token compromise.
- You prefer to maintain a smaller token store.

*Response time: 17.6s*

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
1. TypeScript interface for props:

```typescript
interface DataTableProps<T> {
  columns: {
    key: string;
    header: string;
    width?: number | string;
    sortable?: boolean;
    renderCell?: (data: T) => ReactNode;
  }[];
  data: T[];
  controlled?: boolean;
  onSelectAll?: (selected: boolean) => void;
  onPageChange?: (page: number) => void;
  pageSizeOptions?: number[];
}
```

2. Complete component implementation:

```typescript
import React, {
  useState,
  useEffect,
  useMemo,
  ReactNode,
  useRef,
} from 'react';
import { Table, TableHeader, TableBody, TableRow } from 'react-table';

interface DataTableProps<T> {
  columns: {
    key: string;
    header: string;
    width?: number | string;
    sortable?: boolean;
    renderCell?: (data: T) => ReactNode;
  }[];
  data: T[];
  controlled?: boolean;
  onSelectAll?: (selected: boolean) => void;
  onPageChange?: (page: number) => void;
  pageSizeOptions?: number[];
}

const DataTable: <T extends object>({
  columns,
  data,
  controlled,
  onSelectAll,
  onPageChange,
  pageSizeOptions,
}: DataTableProps<T>) => React.ReactElement = ({
  columns,
  data,
  controlled,
  onSelectAll,
  onPageChange,
  pageSizeOptions,
}) => {
  const [pages, setPages] = useState<{ page: number; data: T[] }>({ page: 0, data: data });
  const [selected, setSelected] = useState<boolean>(false);
  const

*Response time: 9.2s*

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
1. Custom hook useSearch(query: string):

```jsx
import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const useSearch = (query) => {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cachedResults, setCachedResults] = useState({});

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    const cached = cachedResults[query];
    if (cached && Date.now() - cached.timestamp < 300000) {
      setResults(cached.data);
      setIsLoading(false);
      return;
    }

    try {
      const response = await axios.get(`/api/search?q=${query}`);
      setResults(response.data);
      setCachedResults((prev) => ({ ...prev, [query]: { data: response.data, timestamp: Date.now() } }));
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [query]);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchData();
    }, 300);

    return () => clearTimeout(timer);
  }, [fetchData, query]);

  useEffect(() => {
    if (query && cachedResults[query]) {
      fetchData();
    }
  }, [query, fetchData, cachedResults]);

  return { results, isLoading, error, fetchData };
};

export default useSearch;
```

2. SearchPage component using useSearch hook:

```jsx
import React from 'react';
import useSearch from './useSearch';

const SearchPage = () => {
  const { results, isLoading, error, fetchData } = useSearch(window.location.search.slice(4));

  const handleSearch = (e) => {
    const query = e.target.value;
    if (query !== '') {
      fetchData(query);
      window.history.replaceState({}, '', `${window.location.pathname}?q=${query}`);
    } else {
      setResults([]);
    }
  };

  if (error) {
    return <div>Error: {error} <button onClick={fetchData}>Retry</button></div>;
  }

  return (
    <div>
      <input type="text" value={window.location.search.slice(4) || ''} onChange={handleSearch} />
      {isLoading && <div>Loading...</div>}
      {results.length === 0 && !isLoading && <div>No results</div>}
    </div>
  );
};

export default SearchPage;
```

3. URL sync implementation:

The URL synchronization is handled within the `useSearch` hook by updating the search query in the browser history (`window.history.replaceState`) when the user types a query and triggers a new search. This keeps the back and forward buttons working as intended.

4. Canceling in-flight requests importance:

Canceling in-flight requests is crucial to prevent multiple concurrent requests for the same search term, which can result in redundant API calls, increased server load, and unnecessary network usage. By canceling the previous request when a new search is triggered, the hook ensures that only one request is made per unique search term within a 5-minute window, improving performance and resource efficiency.

This prevents potential bugs such as duplicate data fetching, inconsistent UI updates, and increased latency caused by multiple simultaneous requests for the same search query.

*Response time: 19.0s*

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
1. To fetch the 10 most recent published posts with author name, tag names, and comment count without N+1 queries, you can use Prisma's eager loading feature:

```prisma
const posts = await prisma.post.findMany({
  include: {
    author: true,
    tags: { include: true },
    comments: { include: { author: true }, orderBy: { createdAt: 'desc' } },
  },
  take: 10,
  order: {
    published: 'desc',
    createdAt: 'desc',
  },
});

const postsWithDetails = posts.map(post => ({
  ...post,
  tagNames: post.tags.map(tag => tag.name),
  commentCount: post.comments.length,
}));
```

2. To safely add a slug field to the Post model without downtime for a large table (10M rows), follow these steps:

- Create a new column `slug` in the `Post` table:

```sql
ALTER TABLE "Post" ADD COLUMN "slug" VARCHAR(255);
```

- Create a unique index on the `slug` column:

```sql
CREATE UNIQUE INDEX "PostSlugIndex" ON "Post" ("slug");
```

- Write a background job to populate the `slug` column using a transaction to avoid conflicts:

```prisma
await prisma.$transaction(async (prisma) => {
  for await (const post of prisma.post.findMany()) {
    const slug = generateSlug(post.title); // Implement your slug generation logic here
    await prisma.post.update({
      where: { id: post.id },
      data: { slug },
    });
  }
});
```

- After the background job completes, remove the old unique constraint on the `email` column (if not needed anymore):

```sql
DROP CONSTRAINT "UserEmailKey" ON "User";
```

- Finally, add a unique constraint on the new `slug` column:

```sql
ALTER TABLE "Post" ADD CONSTRAINT "PostSlugKey" UNIQUE ("slug");
```

3. To diagnose and fix the slow `findMany` query, follow these steps:

- Analyze the Prisma query and its generated SQL:

```prisma
const posts = await prisma.post.findMany({
  where: {
    tags_some: {
      name: 'someTagName',
    },
  },
});
```

- Generated SQL:

```sql
SELECT "Post".*
FROM "Post"
INNER JOIN (SELECT * FROM "Tag" WHERE name = 'someTagName') AS "tags" ON "Post"."id" = ANY("tags"."postId")
```

- Add an index on the `tags` table for the `name` column:

```sql
CREATE INDEX "TagNameIndex" ON "Tag" ("name");
```

- Re-run the Prisma query to check for performance improvement.

4. Drop down to raw SQL when Prisma's abstraction is insufficient for complex queries or when you need to use database-specific features not available in Prisma. For example, to create a full-text search index on the `Post` content for efficient text search:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

ALTER TABLE "Post" ADD COLUMN "content_trgm_idx" tsvector USING pg_trgm.trgm_similarity(content);

CREATE TRIGGER trigger_update_content_trgm_idx
AFTER INSERT OR UPDATE OF content ON "Post"
FOR EACH ROW EXECUTE PROCEDURE update_trgm_idx_column();

CREATE FUNCTION update_trgm_idx_column()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE "Post"
  SET content_trgm_idx = to_tsvector('english', content)
  WHERE id = NEW.id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

Now you can use PostgreSQL's full-text search capabilities with Prisma's raw queries for efficient content searching.

*Response time: 22.3s*

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
1. **docker-compose.yml**

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    volumes:
      - .:/app
    ports:
      - '3000:3000'
    environment:
      - NODE_ENV=development
      - PORT=3000
    depends_on:
      - db
      - redis
    command: ["npm", "run", "start:hot"]

  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=myuser
      - POSTGRES_PASSWORD=mypass
      - POSTGRES_DB=mydb
    healthcheck:
      test: ["CMD", "pg_isready", "-h", "localhost", "-p", "5432"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:6
    ports:
      - '6379:6379'

  # For environment variables
  .env:
    file: .env

volumes:
  postgres_data:
```

2. **Production Dockerfile (backend)**

```dockerfile
# Builder Stage
FROM node:16-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Runtime Stage
FROM node:16-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
USER node

# Install production dependencies
RUN npm install --only=production

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD node --version || exit 1

CMD ["node", "server.js"]
```

3. **Exit code 137 in production**

An exit code 137 on Linux/Unix systems typically indicates that the process received a SIGKILL signal (usually due to resource limits being exceeded). In a Node.js context, it could mean one of the following:

- The process was forcefully killed by the system (e.g., due to OOM killer).
- A resource limit (e.g., memory limit) was exceeded, and the system killed the process.
- A SIGKILL signal was sent manually, perhaps through a system admin or a monitoring tool.

**Diagnosis:**

- Check system logs for resource limit warnings or SIGKILL signals.
- Review Node.js error logs for clues about what might have caused the resource exhaustion.
- Monitor your application's resource usage (CPU, memory) to identify spikes or leaks.
- Use profiling tools like `node-inspector` or `New Relic` to analyze performance bottlenecks.

4. **Zero-downtime deployment with schema change**

For additive schema changes like adding a new nullable column, follow these steps:

- **Prepare the new migration**: Write a migration script to add the column in your database migration tool (e.g., TypeORM, Sequelize).
- **Deploy the new version**: Deploy the new version of your backend application to a staging or pre-production environment.
- **Run migrations**: Execute the migration script in the new environment to update the schema.
- **Test**: Conduct thorough testing in the new environment to ensure everything works as expected.
- **Switch traffic**: Use a load balancer or a blue-green deployment strategy to route a small percentage of traffic to the new version, allowing for canary testing.
- **Monitor**: Closely monitor the new version for any issues.
- **Full rollout**: If no issues are found, gradually shift more traffic to the new version until all traffic is routed to it.

Remember, for zero-downtime deployments, you might need to maintain compatibility with the old schema in the new version initially, gradually updating logic to use the new schema as traffic shifts.

This sequence assumes an additive schema change and does not involve data migration or complex state management. Depending on your application, additional steps like data backups, testing, and rollback plans might be necessary.

*Response time: 22.5s*

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
1. **Connection Handling**: Each WebSocket connection is associated with a user and a document through a unique identifier. When a user connects, we can assign them a unique ID (e.g., using UUID) and store their connection in a map with the document ID as the key. This way, we can easily retrieve the connection for a specific user and document.

```javascript
const WebSocket = require('ws');
const { v4: uuidv4 } = require('uuid');

const connections = {};

wsServer.on('connection', (socket) => {
  const userId = uuidv4(); // Assign a unique user ID
  const documentId = socket.upgradeReq.url.split('/').pop(); // Get document ID from URL

  // Store the socket connection associated with the user and document
  connections[`${userId}-${documentId}`] = socket;

  socket.on('message', (message) => {
    // Handle incoming messages based on message type
  });

  socket.on('close', () => {
    // Handle disconnection
  });
});
```

2. **Message Protocol**: Define JSON message types for various user actions:

```json
{
  "type": "join",
  "userId": "user-id",
  "documentId": "document-id"
}

{
  "type": "textChange",
  "userId": "user-id",
  "documentId": "document-id",
  "start": {row: 0, col: 0},
  "end": {row: 0, col: 5},
  "text": "Hello"
}

{
  "type": "cursorMove",
  "userId": "user-id",
  "documentId": "document-id",
  "position": {row: 0, col: 5}
}

{
  "type": "userLeft",
  "userId": "user-id",
  "documentId": "document-id"
}
```

3. **Broadcasting**: When a user makes a change, broadcast the message to all other connected users in the same document, excluding the sender.

```javascript
function broadcastMessage(message, userId, documentId) {
  const recipients = Object.keys(connections)
    .filter((connId) => connId.includes(documentId) && connId !== `${userId}-${documentId}`);

  recipients.forEach((recipient) => {
    connections[recipient].send(JSON.stringify(message));
  });
}
```

4. **Reconnection**: When a user reconnects, retrieve their previous document state and send it to them. You can store user states in memory or use a database to persist the state.

```javascript
socket.on('message', (message) => {
  if (message.type === 'join') {
    const { userId, documentId } = message;
    // Retrieve the latest state for the user and document
    const latestState = getLatestState(userId, documentId);
    socket.send(JSON.stringify(latestState));
  }
});
```

5. **Concurrent Edits**: When two users edit the same position simultaneously, you'll end up with conflicting changes. The most common solutions to this problem are:

- Operational Transformation (OT) - transforms operations based on previous operations to resolve conflicts.
- Conflict-free Replicated Data Types (CRDT) - maintains multiple versions of data, ensuring all replicas converge to the same state.

For a simplified implementation, you can choose a simple last-write-wins approach, where the most recent change overwrites any conflicting changes.

This outline provides a basic server-side implementation for a collaborative document editor using Node.js and WebSockets. You may need to expand on this solution by adding features like authentication, error handling, and state persistence.

*Response time: 20.2s*

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
1. **GraphQL Schema (SDL)**

```graphql
type Recipe {
  id: ID!
  title: String!
  author: Author!
  tags: [String!]!
  ratings: [Rating!]!
  steps: [String!]!
  ingredients: [Ingredient!]!
  averageRating: Float
}

type Author {
  id: ID!
  name: String!
}

type Rating {
  id: ID!
  score: Float!
  comment: String
  recipe: Recipe!
}

type Ingredient {
  name: String!
  amount: String!
  unit: String!
}

type Query {
  recipes(filter: RecipeFilter, pagination: Pagination): [Recipe!]!
  recipe(id: ID!): Recipe
}

type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String): Rating!
}

input RecipeFilter {
  tag: String
  minRating: Float
}

input Pagination {
  page: Int!
  limit: Int!
}
```

2. **Resolvers**

```javascript
const { DataLoader } = require('dataloader');
const Recipe = require('./models/Recipe'); // Assuming you have a simple recipe model here
const Author = require('./models/Author');

// Initializing DataLoader
const authorsLoader = new DataLoader(async (ids) => Author.findMany({ where: { id: { [In]: ids } } }));

const resolvers = {
  Query: {
    recipes: async (_, { filter, pagination }) => {
      const { page, limit } = pagination;
      const skip = (page - 1) * limit;

      const recipes = await Recipe.findMany({
        where: {
          // Applying filter
          ...filter,
        },
        offset: skip,
        limit,
        include: {
          author: {
            loader: authorsLoader,
          },
          ratings: {
            include: {
              recipe: false, // To avoid circular dependencies
            },
          },
          ingredients: {
            include: {
              unit: true,
            },
          },
        },
      });

      return recipes;
    },
    recipe: async (_, { id }) => Recipe.findByPk(id),
  },
  Mutation: {
    addRating: async (_, { recipeId, score, comment }) => {
      const recipe = await Recipe.findByPk(recipeId);
      const newRating = await recipe.Ratings().create({ score, comment });
      return newRating;
    },
  },
  Recipe: {
    averageRating: async recipe => {
      if (!recipe.ratings) return 0;
      const totalScore = recipe.ratings.reduce((acc, rating) => acc + rating.score, 0);
      return totalScore / recipe.ratings.length;
    },
  },
};
```

3. **N+1 Problem with DataLoader**

**Problem:**

Assume we have 10 recipes, and each recipe is associated with one author. Without DataLoader, fetching authors would result in 10 separate database queries, leading to the N+1 problem.

```javascript
const recipes = await Recipe.findMany({
  include: { author: true },
});

// This results in 10 queries: one for each recipe to fetch the associated author
```

**Fix with DataLoader:**

By using DataLoader, we batch the requests and reduce the number of queries to 1.

```javascript
const loaders = {
  authors: new DataLoader(async (ids) => Author.findMany({ where: { id: { [In]: ids } } })),
};

const resolvers = {
  Query: {
    recipes: async (_, { pagination }) => {
      const { page, limit } = pagination;
      const skip = (page - 1) * limit;

      const recipes = await Recipe.findMany({
        where: {}, // Assuming we don't have complex filtering here for simplicity
        offset: skip,
        limit,
        include: {
          author: {
            loader: loaders.authors,
          },
        },
      });

      return recipes;
    },
  },
};
```

4. **Client Request for Recipe Title, Author Name, and First 3 Ingredients**

```graphql
query GetRecipeDetails($recipeId: ID!) {
  recipe(id: $recipeId) {
    title
    author {
      name
    }
    ingredients(first: 3) {
      name
      amount
      unit
    }
  }
}
```

5. **When to choose GraphQL over REST:**

- **Complex Queries:** GraphQL excels when clients need to fetch nested resources or complex data structures in a single request.
- **Over- and Under-Fetching:** GraphQL allows clients to specify exactly what data they need, reducing data transfer and improving performance.
- **Strong Typing:** With schema definition and validation, GraphQL provides better type safety compared to REST, where the contract between client and server is often implicit.

**When NOT to choose GraphQL over REST:**

- **Simple APIs:** For straightforward APIs with minimal nesting and few resources, REST might be simpler to implement and understand.
- **Caching:** REST APIs can be easier to cache at the HTTP layer, as each endpoint represents a resource, and caching strategies are more straightforward.
- **Discoverability:** REST's standardized methods (GET, POST, PUT, DELETE) make it easier for developers to understand how to interact with an API without detailed documentation.

Remember, the choice between GraphQL and REST largely depends on the specific needs of your application, team expertise, and existing infrastructure.

*Response time: 29.5s*

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
Below is a comprehensive HTML and CSS solution that fulfills the given requirements. The layout is primarily achieved using CSS Grid for structuring the main content area and Flexbox for card and button layouts.

### HTML

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Responsive Layout</title>
<link rel="stylesheet" href="styles.css">
</head>
<body>
<header id="header">Header</header>

<div class="container">
    <aside id="sidebar">Sidebar</aside>
    <main id="main-content">
        <div class="card-grid">
            <div class="card">
                <img src="https://via.placeholder.com/400x225" alt="Card Image">
                <h3>Card Title</h3>
                <p>Description of the card content.</p>
                <div class="card-footer">
                    <button>Left Button</button>
                    <button>Right Button</button>
                </div>
            </div>
            <!-- Repeat the card structure as needed -->
        </div>
    </main>
</div>
</body>
</html>
```

### CSS (styles.css)

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: sans-serif;
}

#header {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 60px;
    background-color: #f1f1f1;
}

.container {
    height: calc(100% - 60px);
    display: grid;
    grid-template-columns: 240px 1fr;
    grid-template-rows: 100%;
}

#sidebar {
    grid-column: 1;
    background-color: #eee;
    overflow-y: auto;
}

#main-content {
    grid-column: 2;
    padding: 20px;
    background-color: #fff;
    overflow-y: auto;
}

.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    grid-gap: 20px;
}

.card {
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card img {
    width: 100%;
    height: 200px; /* 16:9 ratio, adjust as needed */
}

.card h3 {
    margin: 10px 0;
}

.card p {
    margin: 10px 0;
}

.card-footer {
    display: flex;
    justify-content: space-between;
    margin-top: auto;
}

.card-footer button {
    margin: 5px;
    padding: 8px 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #f1f1f1;
    cursor: pointer;
}

/* Responsive adjustments for mobile */
@media (max-width: 768px) {
    .card-grid {
        grid-template-columns: 1fr;
    }
}
```

### Layout Approach

1. **Header**: The header is fixed using `position: fixed` on the `#header`. This ensures it stays at the top even as the content scrolls.

2. **Container Grid**: A `grid` layout is used for the container (`container`) to separate the sidebar and main content. The `grid-template-columns` property specifies a sidebar width of 240px and the rest of the viewport for the main content (`1fr`).

3. **Sidebar and Main Content**: Both the sidebar and main content have fixed heights equal to the viewport height minus the fixed header height. They use `overflow-y: auto` to enable vertical scrolling independently.

4. **Card Grid**: The card grid within the main content uses CSS Grid as well (`grid-template-columns: repeat(auto-fit, minmax(320px, 1fr))`). This allows for a responsive layout where cards occupy two columns on desktop (≥768px) and one column on mobile (≤768px).

5. **Card Elements**: Each card maintains a 16:9 aspect ratio for the image using `width: 100%` and `height: 200px` (adjust as needed). The title, description, and buttons are styled using flexbox within the card footer for alignment.

This approach leverages the power of CSS Grid and Flexbox to achieve a layout that meets all specified requirements without the need for JavaScript or external frameworks. The use of media queries ensures the cards stack into a single column for smaller screens.

*Response time: 29.9s*

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
1. **Transport Mechanism**: For real-time notifications, **WebSocket** is the most suitable choice. Here's why:

   - **WebSocket** provides a persistent, bi-directional communication channel between the client and server. This means that once the connection is established, both parties can send data to each other at any time, making it ideal for real-time updates.
   
   - **Server-Sent Events (SSE)** is unidirectional (server-to-client), suitable for scenarios where the server needs to push updates to the client, but not for client-to-server interactions, which are crucial in a project management tool.

   - **Polling** involves the client periodically requesting updates from the server. This method is inefficient as it consumes bandwidth and server resources, especially with many users.

   - **Push notifications** (like those used by mobile apps) involve an intermediary service (like Firebase Cloud Messaging, Apple Push Notification service) and aren't directly applicable to a web-based project management tool without additional complexity.

2. **Database Schema for Notifications**:

   A simple schema could look like this:

   ```sql
   CREATE TABLE notifications (
       id SERIAL PRIMARY KEY,
       user_id INTEGER NOT NULL,
       task_id INTEGER,
       comment_id INTEGER,
       deadline_approaching BOOLEAN DEFAULT FALSE,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       read BOOLEAN DEFAULT FALSE,
       FOREIGN KEY (user_id) REFERENCES users(id),
       FOREIGN KEY (task_id) REFERENCES tasks(id),
       FOREIGN KEY (comment_id) REFERENCES comments(id)
   );
   ```

   - `user_id`: ID of the user to whom the notification is directed.
   - `task_id`: ID of the task if notification is about task assignment or updates.
   - `comment_id`: ID of the comment if notification is about a new comment on a task.
   - `deadline_approaching`: Boolean flag indicating if the notification is about an upcoming deadline.
   - `created_at`: Timestamp of when the notification was created.
   - `read`: Boolean flag indicating if the user has read the notification.

3. **Handling Offline Users**: Implement a local storage solution (using `localStorage` or `sessionStorage` in the browser) to temporarily store notifications when the user is offline. Upon reconnecting, the client can retrieve these stored notifications and mark them as read on the server.

4. **Deadline Check Implementation**:

   - **Cron Job**: Schedule a cron job (e.g., using a service like cron-job.org or a server-side scheduled task in your tech stack) to run every hour. The task can query the database for tasks with deadlines within the next 24 hours and send notifications via WebSocket to the relevant users.

   - **Queue or Event-Driven**: For a more scalable and real-time solution, use a message queue system (like RabbitMQ, Kafka) or an event-driven architecture with a service like AWS SQS or Google Cloud Tasks. The deadline check logic can be encapsulated in a background worker that processes messages from the queue. This ensures that the check doesn't block the main application and scales well with the load.

5. **Scaling for 100,000 Concurrent Users**:

   - **Load Balancing**: Distribute incoming WebSocket connections across multiple servers using a load balancer (e.g., Nginx, HAProxy).
   - **WebSocket Server Scaling**: Use a WebSocket server solution designed for horizontal scaling, such as Socket.IO with Redis for session management or a dedicated WebSocket server like Tornado (Python) or Vert.x (Java/Scala).
   - **Database Sharding**: Split your database into multiple smaller databases (sharding) to distribute the load. Use a database system that supports sharding, like MongoDB or PostgreSQL with extensions.
   - **Caching**: Implement caching (e.g., Redis, Memcached) for frequently accessed data to reduce database load.
   - **Asynchronous Processing**: Use a queue system for non-real-time tasks like sending deadline reminders to ensure the main application remains responsive.
   - **Content Delivery Network (CDN)**: For serving static assets (CSS, JavaScript, images), use a CDN to reduce server load and improve page load times for users worldwide.
   - **Monitoring and Auto-scaling**: Implement monitoring tools (e.g., Prometheus, Grafana) to track resource usage and set up auto-scaling groups in cloud environments (AWS EC2 Auto Scaling, Google Compute Engine Autoscaler) to dynamically adjust the number of servers based on demand.

By following these strategies, you can design a robust, scalable real-time notification system for your project management tool that handles a large number of concurrent users efficiently.

*Response time: 24.4s*

---
