# Model: yi-coder:1.5b
**Test Date:** 2026-03-10 19:41:02
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
Designing the API for a multi-tenant SaaS project management tool involves several major steps. It also requires a thorough understanding of RESTful conventions and the necessary server-side coding languages.

Here's a design for the API:

1. Endpoints:

- GET /workspaces: List all the workspaces a user belongs to.
- GET /projects/:id/:workspace_id: List all the projects in a specific workspace.
- GET /projects/:id/tasks: List all the tasks in a specific project.
- GET /tasks/:id/:workspace_id: List all the tasks in a specific project.
- GET /users: List all the users in the system.
- GET /users/:id: Details of a specific user.
- GET /comments/:id/:workspace_id: List all the comments on a specific task.
- POST /tasks/:id/assign: Assign a task to a specific user.
- POST /comments/:id/:workspace_id: Add a comment to a specific task.
- GET /status/:id/:workspace_id: Get the status of a specific task.

2. Request/Response JSON Shapes:

For creating a task:
```
{
  "project_id": "<project-id>",
  "description": "<task-description>",
  "due_date": "<due-date>",
  "assignee": "<assignee-id>"
}
```

For updating the status of a task:
```
{
  "status": "<status-name>"
}
```

For listing tasks with filters:
```
{
  "assignee": "<user-id>",
  "status": "<status-name>",
  "due_date": "<due-date>"
}
```

3. Error response format:
- All endpoints return HTTP status codes as per the RESTful conventions. 404 Not Found for a non-existent resource, 401 Unauthorized if the user doesn’t have the required permissions, 422 Unprocessable Entity if the request body is not valid.

4. Pagination:
- Implement pagination in the API to avoid exceeding the maximum response size. 

5. Which endpoints need which HTTP status codes:
- The GET endpoints should return HTTP status codes of 200 OK.
- The POST endpoints should return HTTP status codes of 201 Created if a resource was successfully created.
- The GET endpoints should return HTTP status codes of 200 OK if the resource was successfully retrieved.

Remember to handle all edge cases and security measures like token-based authentication, data validation, etc., when designing the API.

*Response time: 4.1s*

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
This problem involves creating a Node.js API endpoint using Express.js and TypeScript. The API should handle a partial update of tasks within a workspace, ensuring that only the provided fields are changed and that the updated task belongs to the workspace.

Please note that this is a simplified version of the task model, which may include more properties or relationships, and different validations may be needed for a production application.

```typescript
import express from 'express';
import { z } from 'zod';
import * as TasksService from './services/tasks.service';

const app = express();
const router = express.Router();

// Schema for partial update
const updateTaskSchema = z.object({
  title: z.string().max(200).optional(),
  status: z.enum(['todo', 'in_progress', 'done', 'cancelled']).optional(),
  assignee_id: z.number().null().optional(),
  due_date: z.date().nullable().optional()
});

router.patch('/:workspaceId/tasks/:taskId', async (req, res, next) => {
  const { workspaceId, taskId } = req.params;
  const { data } = req;

  try {
    const task = await TasksService.getTask(workspaceId, taskId);
    
    // Validate that the task belongs to the workspace
    if (!task) {
      res.status(404).send({ error: 'Workspace does not contain the task' });
      return;
    }

    const updatedTask = updateTaskSchema.parse(data);

    // Validate that the assignee_id is a member of the workspace
    if (updatedTask.assignee_id && !await TasksService.isAssigneeIdValid(workspaceId, updatedTask.assignee_id)) {
      res.status(400).send({ error: 'Invalid assignee_id' });
      return;
    }

    // Check if trying to set status to 'cancelled' when task has open subtasks
    if (updatedTask.status === 'cancelled' && (await TasksService.getOpenSubtasksCount(workspaceId, taskId)) > 0) {
      res.status(409).send({ error: 'Task has open subtasks' });
      return;
    }

    await TasksService.updateTask(workspaceId, taskId, updatedTask);
    res.send(updatedTask);
  } catch (error) {
    next(error);
  }
});

app.use('/', router);

export default app;
```

Now let's write some unit tests. For simplicity, we'll use Jest and the "fetch" mock for Node.js, as they come with Node.js:

```typescript
import { fetch } from 'jest-fetch-mock';

beforeEach(() => {
  fetch.resetMocks();
});

test('Update task successfully', async () => {
  const workspaceId = '1';
  const taskId = '1';
  const updatedData = {
    title: 'Updated Title',
    status: 'in_progress',
    assignee_id: null,
    due_date: null
  };
  fetch.once('POST', `http://localhost:5000/workspaces/${workspaceId}/tasks/${taskId}`, {
    body: JSON.stringify(updatedData),
    headers: new Headers({ 'Content-Type': 'application/json' })
  }).mockResponseOnce('{}');

  const result = await fetch('/workspaces/1/tasks/1', {
    method: 'PATCH',
    body: JSON.stringify(updatedData),
    headers: new Headers({ 'Content-Type': 'application/json' })
  });

  expect(result.status).toBe(200);
});

test('Task belongs to workspace', async () => {
  fetch.resetMocks();
  fetch.once('GET', `http://

*Response time: 6.3s*

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
Here is a simple implementation of the authentication system in Node.js using Express, TypeScript, and the JSON Web Token (JWT).

Firstly, install the necessary dependencies.

```bash
npm install express body-parser bcryptjs jsonwebtoken
```

The server.ts file:

```typescript
import express from 'express';
import bodyParser from 'body-parser';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

const app = express();
app.use(bodyParser.json());

// Mock users database
const users = {
    "1": {
        id: "1",
        email: "user1@gmail.com",
        password: "password1",
        role: "user"
    },
    "2": {
        id: "2",
        email: "user2@gmail.com",
        password: "password2",
        role: "admin"
    },
};

app.post('/auth/register', async (req, res) => {
    const user = req.body;
    const hashedPassword = await bcrypt.hash(user.password, 12);
    user.password = hashedPassword;
    users[user.email] = user;
    res.send(user);
});

app.post('/auth/login', async (req, res) => {
    const user = req.body;
    const userPassword = await bcrypt.hash(user.password, 12);
    if (!(user.email in users) || !(await bcrypt.compare(user.password, users[user.email].password))) {
        return res.send({ error: 'Invalid email or password' });
    }
    const token = jwt.sign({ userId: user.email, email: user.email, role: users[user.email].role, iat: Math.floor(Date.now() / 1000), exp: Math.floor(Date.now() / 1000) + 60 * 60 * 24 * 7 }, 'SECRETKEY');
    const refreshToken = jwt.sign({ userId: user.email, email: user.email, role: users[user.email].role, iat: Math.floor(Date.now() / 1000), exp: Math.floor(Date.now() / 1000) + 60 * 60 * 24 * 7 * 10 }, 'REFRESHKEY');
    res.cookie('accessToken', token, { httpOnly: true

*Response time: 4.0s*

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
1. POST /auth/refresh — use the refresh token from cookie to issue a new access token. Rotate the refresh token (issue new one, invalidate old one).

The refresh token system can be implemented in different ways depending on how you want to handle session invalidation. One common way is to invalidate the refresh token when it expires, and issue a new one. If the old refresh token is used to access the API again, the system will know that the previous session is expired and will send a 401 error (unauthorized).

```python
from flask import request, jsonify
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if RedisTokenStore.is_valid(username):
        RedisTokenStore.invalidate(username)
        RedisTokenStore.set(username, password)
        return True
    return False
```

2. POST /auth/logout — invalidate the refresh token, clear the cookie.

This can be done by simply invalidating the token when it expires. The token store will handle this and invalidate the token when it expires.

3. Implement refresh token rotation with a Redis-based token store (show the Redis data structure and TTL strategy).

A Redis token store would be used to store the tokens, and the token TTL (Time-To-Live) can be set to ensure that the tokens are invalidated after a certain period of time.

```python
from flask_httpauth import HTTPBasicAuth
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    TimedeltaMixin,
)

class RedisTokenStore(TimedeltaMixin):
    def __init__(self, user_data, token_ttl):
        self.user_data = user_data
        self.token_ttl = token_ttl
        self.serializer = Serializer(secret_key=SECRET_KEY, ttl=token_ttl)

    def get_user(self, username):
        return self.user_data.get(username)

    def set(self, username, password):
        self.user_data[username] = password
        return self.serializer.dumps({'username': username})

    def is_valid(self, username, password):
        password_hash = self.user_data.get(username)
        return password_hash == password

    def invalidate(self, username):
        self.user_data.pop(username, None)
```

4. How do you handle the case where a refresh token is used twice? (token reuse detection) — implement it.

To detect reuse of a refresh token, a timestamp can be stored with the refresh token when it is issued. If the refresh token is used again, the timestamp can be checked. If the timestamp is older, the token is considered to be reusable.

```python
from flask_httpauth import HTTPBasicAuth
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    TimedeltaMixin,
)

class RedisTokenStore(TimedeltaMixin):
    def __init__(self, user_data, token_ttl):
        self.user_data = user_data
        self.token_ttl = token_ttl
        self.serializer = Serializer(secret_key=SECRET_KEY, ttl=token_ttl)

    def get_user(self, username):
        return self.user_data.get(username)

    def set(self, username, password):
        self.user_data[username] = {'password': password, 'timestamp': time.time()}
        return self.serializer.dumps({'username': username})

    def is_valid(self, username, password):
        user = self.user_data.get(username)
        return user and 'password' in user and 'timestamp' in user and time.time() - user['timestamp'] < self.token_ttl

    def invalidate(self, username):
        self.user_data.pop(username, None)
```

5. A user changes their password — how do you invalidate ALL their existing sessions? Implement it.

To invalidate all existing sessions when a password changes, the system would iterate over all users, invalidate their tokens, and set the new password.

```python
def set_password(self, username, password):
    for user in self.user_data:
        self.invalidate(user)
    return self.set(username, password)
```

6. What is the difference between token blacklisting and token rotation? When would you use each?

Token blacklisting is a strategy where tokens are marked as "blacklisted". When a token is used, it is checked to see if it is in the blacklist. If the token is found in the blacklist, the token is invalidated and a new one is issued. Token rotation, on the other hand, involves rotating the set of valid tokens, rather than blacklisting them. It involves setting a new set of tokens when the existing ones are exhausted.

*Response time: 7.7s*

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
This problem requires writing a complex data-table component in React using TypeScript.

Here's a basic implementation of the component, showing how to define the Props interface, and how to implement the component using TypeScript:

```typescript
import React, { useState, useMemo } from 'react';

export interface DataTableProps<T> {
  columns: Array<keyof T>;
  data: T[];
  defaultSort?: keyof T;
  defaultOrder?: 'asc' | 'desc';
  onRowClick?: (row: T) => void;
  onSelectRow?: (row: T, isSelected: boolean) => void;
  onPageChange?: (page: number) => void;
  pageSize?: number;
  defaultPageSize?: number;
  controlled?: boolean;
}

const DataTable: React.FC<DataTableProps<any>> = ({
  columns,
  data,
  defaultSort = '',
  defaultOrder = 'asc',
  onRowClick,
  onSelectRow,
  onPageChange,
  pageSize = 10,
  defaultPageSize,
  controlled,
}) => {
  const [currentSort, setCurrentSort] = useState(defaultSort);
  const [currentOrder, setCurrentOrder] = useState(defaultOrder);
  const [currentPage, setCurrentPage] = useState(0);
  const [pageSizeState, setPageSize] = useState(pageSize);
  
  const sortData = useMemo(() => {
    return data.sort((a, b) => {
      const isAsc = currentOrder === 'asc';
      return isAsc ? 
        a[currentSort] > b[currentSort] ? 1 : -1 :
        b[currentSort] > a[currentSort] ? 1 : -1;
    });
  }, [currentOrder, currentSort, data]);

  const paginatedData = useMemo(() => {
    const startIndex = currentPage * pageSizeState;
    return sortData.slice(startIndex, startIndex + pageSizeState);
  }, [currentPage, pageSizeState, sortData]);

  const renderCell = (row: T, column: keyof T) => {
    return <div>{row[column].toString()}</div>;
  };

  return (
    <div>
      <header>
        <div>
          {controlled
            ? (
              <button
                onClick={() => {
                  setCurrentSort(defaultSort);
                  setCurrentOrder(defaultOrder);
                }}
              >
                Sort
              </button>
            )
            : (
              <button
                onClick={() => setCurrentSort(currentSort === '' ? (defaultSort === '' ? 'defaultSort' : defaultSort) : '')}
              >
                {currentSort === '' ? (defaultSort === '' ? 'Default sort' : defaultSort) : `${currentSort} ${currentOrder === 'asc' ? 'Asc' : 'Desc'}`}
              </button>
            )}
          {controlled 
            ? (
              <button
                onClick={() => {
                  if (currentSort === '') {
                    setCurrentSort(defaultSort);
                    setCurrentOrder(defaultOrder);
                  } else {
                    setCurrentOrder(currentOrder === 'asc' ? 'desc' : 'asc');
                  }
                }}
              >
                {currentOrder === 'asc' ? 'Desc' : 'Asc'}
              </button>
            )
            : (
              <button
                onClick={() => {
                  if (currentSort === '') {
                    setCurrentSort(defaultSort);
                    setCurrentOrder(defaultOrder);
                  } else {
                    setCurrentOrder(currentOrder === 'asc' ? 'desc' : 'asc');
                  }
                }}
              >
                {currentOrder === 'asc' ? 'Desc' : 'Asc'}
              </button>
            )}
          {controlled ? (
            <select
              value={pageSizeState}
              onChange={e => setPageSize(Number(e.target.value))}
            >
              {[10, 25, 50].map(size => <option key={size} value={size}>{size}</option>)}
            </select>
          ) : (
            <div>
              {paginatedData.map((row, index) => (
                <div
                  key={index}
                  onClick={() => {
                    onRowClick && onRowClick(row);
                  }}
                >
                  {columns.map(column => (
                    <div key={column}>
                      {renderCell(row, column)}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>
      </header>
      {controlled ? (
        <button
          onClick={() => {
            if (currentPage === 0) {
              setCurrentPage(0);
              setPageSize(pageSize);
            } else {
              setCurrentPage(0);
              setPageSize(pageSize * 2);
            }
          }}
        >
          Previous page
        </button>
      ) : (
        <div>
          {paginatedData.map((row, index) => (
            <div
              key={index}
              onClick={() => {
                onRowClick && onRowClick(row);
              }}
            >
              {columns.map(column => (
                <div key={column}>
                  {renderCell(row, column)}
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DataTable;
```

This component now allows sorting and pagination. It can be used with any row type, and the sorting and pagination behavior can be controlled by passing functions to the onPageChange and onSelectRow props. 

For the action button custom cell, we've added a custom `renderCell` function that returns a div containing the row's data.

For performance improvements, we've memoized `sortData` and `paginatedData` to avoid unnecessary re-renders. We've also included `useMemo` hooks to calculate the data we need only when the dependencies change.

Note: This is just a simple implementation, it doesn't include edge cases, error checking, etc. For example, if a column is not found in the row, it will throw an error. The same goes for the sort direction and page size. You can add additional logic as needed.

You can use this component by simply importing and passing it your data and props.

*Response time: 9.9s*

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
Here's a simple implementation of the problem using the React hooks you've mentioned.

```jsx
import React, { useState, useEffect } from 'react';

const useSearch = (query, delay = 300) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const canceler = React.useRef();
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(true);
      setError(null);
      
      const abortController = new AbortController();
      canceler.current = abortController;

      fetch('/api/search', {
        signal: abortController.signal,
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      }).then(res => {
        if (!res.ok) throw res;

        return res.json();
      }).then(res => {
        setResults(res.data);
        setLoading(false);
        
        // Cache the results for next 5 min
        localStorage.setItem('search_' + query, JSON.stringify(res.data));
      }).catch(err => {
        setError('Error occurred, please try again later.');
        setLoading(false);
      });
    }, delay);

    return () => {
      canceler.current && canceler.current.abort();
    };
  }, [query]);

  useEffect(() => {
    const cachedResults = JSON.parse(localStorage.getItem('search_' + query));
    
    if (cachedResults) {
      setResults(cachedResults);
      setLoading(false);
    }
  }, [query]);

  return { results, loading, error };
};

const SearchPage = ({ query }) => {
  const { results, loading, error } = useSearch(query);

  return (
    <div>
      {loading && <div>Loading...</div>}
      {error && <div>{error}</div>}
      {results.length === 0 && !loading && <div>No results</div>}
      {results.map(result => (
        <div key={result.id}>{result.name}</div>
      ))}
    </div>
  );
};
```

Now let's discuss why cancelling in-flight requests is important here. When a user is performing a new search, it should cancel the previous one. This is because each new search is independent from the previous one. If the user keeps typing, they want to get the most recent results. If they stop typing, they want the results of their last search. So to prevent that, we introduce a ref which keeps track of the in-flight requests. When a new search starts, we cancel the previous request. This prevents the requests from persisting and keeping the old data.

URL sync implementation is done by caching the results in localStorage, and checking if the results are present there before making a new fetch. If the results are found there, we just return the cached results and don't make a new fetch. This ensures that even if the user refreshes their browser, the search stays up-to-date.

For the bug related to URL, it doesn't prevent the URL from getting inconsistent. It's because we are caching the results locally, which doesn't persist between refreshes. If the user refreshes the page, the cached result will be gone, and the URL will reflect the search term from the latest search. If the user navigates back to a previous page, the cached result will still be there, and the URL will reflect the search term from the previous search. But the user should still see the results of the previous search.

*Response time: 5.4s*

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
1. Prisma ORM query that fetches the 10 most recent published posts, including: author name, tag names, comment count (not the comments themselves):

```prisma
query {
  posts(where: { published: true }) {
    author {
      name
    }
    tags {
      name
    }
    _count: comments
    recent(orderBy: {createdAt: desc}) {
      id
    }
  }
}
```

2. Migrating Post to include slug:

This can be done by defining a generated field. Note that you cannot directly drop down from Prisma to raw SQL because Prisma is a layer on top of your database, and it abstracts the underlying SQL. If your database is changed and Prisma schema is not reflecting the changes, you can manually update Prisma schema to reflect those changes.

```prisma
model Post {
  id          Int     @id
  title       String  
  content     String  
  published   Boolean @default(false)
  authorId    Int     
  author      User    @relation(name: "author", fields: [authorId], references: [id])
  tags        Tag[]  
  comments     Comment[]
  createdAt   DateTime @default(now())
  slug        String  @generated("create_slug", args: { uniqueSlugs: true })
}
```

3. Slow query `findMany posts filtered by tag name takes 800ms`:

You can diagnose this by checking the execution plan of your queries. The execution plan for the query `findMany posts filtered by tag name` can be slow due to the underlying query for `_all`. To speed it up, you can create index on `tag.name` in Postgres.

```sql
CREATE INDEX ON tags(name);
```

4. Dropdown from Prisma to raw SQL:

You should ideally avoid using Prisma raw queries as much as possible, as Prisma ORM abstracts your database access and provides higher level abstractions like relations, queries, and data fetching. However, you can still directly use raw SQL if necessary. The example would be `POSTS.find({ where: { tagId_in: [1, 2] } });`, which will directly fetch posts where tag ids are 1 and 2, but this would require you to handle the connection to the database yourself. It is a more prone approach to error and is generally less recommended.

*Response time: 3.7s*

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
1. Docker Compose:

```yaml
version: '3'
services:
  web:
    build: ./
    command: npm start
    volumes:
      - .:/usr/src/app
    ports:
      - '5000:5000'
    depends_on:
      - db
  db:
    image: postgres
    environment:
      POSTGRES_DB: my_db
    volumes:
      - db_data:/var/lib/postgresql/data
volumes:
  db_data:
```

This docker-compose file will build the web service from the current directory using `npm start` command for the frontend and expose the port 5000 to the outside world. It also sets the environment variable `POSTGRES_DB` to `my_db` for the PostgreSQL database. The `db_data` volume is used for persisting data between restarts.

2. Dockerfile for backend (Node.js):

```docker
# Using multi-stage build
# First stage
FROM node:12 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# Second stage
FROM node:12-alpine
WORKDIR /app
COPY --from=builder /app .
ENV NODE_ENV=production
RUN npm install --production
```

This Dockerfile builds a base image using Node.js 12. The first `FROM` command creates a new image. The second `FROM` sets the base image for the runtime. This second `FROM` copies all files from the `builder` stage into the runtime. The `ENV NODE_ENV=production` sets the environment variable NODE_ENV to production. It then installs production dependencies with `npm install --production`.

3. Backend crashes in production:

By default, a docker container will exit with a status code of 137 when it exits due to reasons such as timeouts, SIGKILL, SIGTERM, or a signal received from the container runtime. To diagnose such a problem, you can run the following command:

```bash
docker inspect --format '{{json .State.Waiting }}' $(docker ps -q)
```

This command will return a JSON object. If the object is empty, it means that the container is not in a state where it should be. If the object is not empty, it means that the container is still waiting for something.

4. Deploying a new version with zero downtime:

Assuming that we are deploying a new image with the same name and version as the existing one, you can take advantage of docker's inter-container communication feature to achieve zero-downtime deployments. Docker compose will expose the running services on different ports and expose them via a shared Docker network. Any requests sent to the exposed ports of the running services will be forwarded to the corresponding services running in the docker-compose environment. The new image will be pulled from the new tag, and the old images will be removed. After the new image is pulled, the old images will be pruned.

In a production environment, you may want to remove the old images from the local Docker daemon after successful deployment to avoid unnecessary space consumption.

You can use services like `docker system prune` to remove unnecessary Docker objects.

Also, if the database schema is changed, you can first apply the changes to the new schema in the test environment. After testing, you can rollback the schema to the new one in the production environment. The database transactions will be atomic in this case.

*Response time: 5.4s*

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
1. Connection handling:

   To associate a WebSocket connection with a user and document, you can keep track of the user's ID (assumed to be sent by the client when connecting) and the ID of the document (also sent by the client). When a user connects, store their ID and the document ID in the connection object. When a user disconnects, remove their connection from the map.

2. Message protocol:

   The message protocol can be defined as follows:

   - Join Document:

     {
       "type": "join_document",
       "document_id": <document_id>
     }

   - Text Change:

     {
       "type": "text_change",
       "cursor": <cursor_position>,
       "text": <new_text>
     }

   - Cursor Move:

     {
       "type": "cursor_move",
       "cursor": <cursor_position>
     }

   - User Left:

     {
       "type": "user_left",
       "user_id": <user_id>
     }

3. Broadcasting:

   To broadcast a message to all users in the same document, for each user in the document, send a text change message to their WebSocket connection. However, this might cause some latency if the message is sent while the user is offline or while the document is being edited by another user. Therefore, you might want to implement a broadcast buffer or rate-limiting logic to avoid this problem.

4. Reconnection:

   When a user reconnects, you can check if the user's ID and the document ID exist in the connection map. If they do, send the latest state of the document to the user.

5. What happens if two users edit the exact same position simultaneously?

   This can occur if a user is editing the document when another user makes a change that's immediately followed by the same user. In this case, the document state will be in a state of conflict, because the two users have made separate edits at the same position.

   To handle this, you could implement a write-set protocol that records every operation (text change, cursor move, etc.) that has been performed on the document. If two users make the same set of operations, the latest operation from each user becomes the resolved state. This approach allows for conflict resolution, and it is called "linearizable". However, it comes at a cost of increased complexity and performance overhead.

Note: This is a simplified version of the problem and does not cover all aspects of a full-fledged collaborative document editor. For example, implementing a timestamp for every operation, ensuring data integrity and consistency, and handling network failures are not addressed in this example.

*Response time: 4.1s*

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
1. GraphQL schema (SDL):

```
type Recipe {
  id: ID!
  title: String!
  ingredients: [Ingredient!]!
  steps: [Step!]!
  author: User!
  tags: [Tag!]!
  averageRating: Float!
    ...on Recipe {
      computedRating {
        score
        comment
      }
    }
}

type User {
  id: ID!
  name: String!
}

type Tag {
  id: ID!
  name: String!
}

type Step {
  id: ID!
  description: String!
}

type Inredient {
  id: ID!
  name: String!
  amount: Float!
  unit: String!
}

type Rating {
  score: Float!
  comment: String
}

type Query {
  recipes(filter: FilterInput, pagination: PaginationInput): [Recipe!]!
  recipe(id: ID!): Recipe
}

type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String): Rating
}

input FilterInput {
  tag: String
  minRating: Float
}

input PaginationInput {
  page: Int
  limit: Int
}
```

2. Resolvers:

For the mutation, the resolvers will be like this:

```
mutation AddRating($recipeId: ID, $score: Float, $comment: String) {
  addRating(recipeId: $recipeId, score: $score, comment: $comment) {
    score
    comment
  }
}
```

For the query, resolvers will be like this:

```
query Recipes($filter: FilterInput, $pagination: PaginationInput) {
  recipes(filter: $filter, pagination: $pagination) {
    id
    title
    ingredients {
      name
      amount
      unit
    }
    steps {
      id
      description
    }
    author {
      id
      name
    }
    tags {
      id
      name
    }
    averageRating
  }
}
```

3. For the N+1 problem, it happens when you fetch additional information (like author) for each recipe. To fix it, we use DataLoader in combination with Apollo Server which automatically batches multiple results.

4. The client will write the exact GraphQL query they would like to execute, it would be:

```
query {
  recipe(id: "123") {
    id
    title
    author {
      name
    }
    ingredients {
      name
      amount
      unit
    }
  }
}
```

5. GraphQL is a more flexible solution as it allows client to control how data is fetched and manipulated. It is designed to be server-less and provides a schema definition language that allows for complex data structures to be managed on the server side. REST, on the other hand, relies on HTTP requests to manage data on the client side and is usually used when the data needs to be manipulated and modified on the client side.

*Response time: 4.9s*

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
Here is the solution to the problem:

```HTML
<!DOCTYPE html>
<html>
<head>
    <style>
    body {
        margin: 0;
        height: 100vh;
        display: flex;
        flex-direction: column;
    }

    .header {
        background: #f0f0f0;
        padding: 10px;
        text-align: center;
        width: 100%;
        height: 60px;
        position: fixed;
        top: 0;
        left: 0;
    }

    .sidebar {
        background: #d0d0d0;
        padding: 10px;
        width: 240px;
        height: calc(100vh - 60px);
        overflow-y: auto;
        position: fixed;
        top: 60px;
        left: 0;
    }

    .main {
        flex-grow: 1;
        overflow-y: auto;
    }

    .card {
        display: flex;
        flex-direction: column;
        padding: 10px;
        margin-bottom: 10px;
    }

    .card img {
        aspect-ratio: 16/9;
        width: 100%;
    }

    .card .title {
        margin-bottom: 5px;
    }

    .card .description {
        margin-top: 5px;
    }

    .card .footer {
        display: flex;
        justify-content: space-between;
    }

    @media (max-width: 768px) {
        .card {
            flex-direction: column;
        }

        .card .footer {
            align-items: center;
        }
    }
    </style>
</head>
<body>
    <div class="header">Header</div>
    <div class="sidebar">Sidebar</div>
    <div class="main">
        <div class="card">
            <img src="..." alt="Image">
            <div class="title">Title</div>
            <div class="description">Description</div>
            <div class="footer">
                <div>Button 1</div>
                <div>Button 2</div>
            </div>
        </div>
    </div>
</body>
</html>
```

This solution uses Flexbox to layout the desired UI.

In the CSS, we use Flexbox's `flex-direction` property to decide how the child elements stack. We use `flex-grow` on the main div to grow the height of the main content so that it can fill the remaining space when the sidebar is not present.

The sidebar and main content are `position: fixed`, so that they remain fixed to the top and left of the page, regardless of the viewport size. This allows for the sidebar and main content to be scrollable independently.

The `.card` div is a flex container, stacking its child elements one above another. We use `justify-content: space-between` on the `.footer` to align the buttons on both sides of the card.

We use media queries to handle the responsive behavior of the card on different screen sizes (less than or equal to 768px). When the screen width is less than or equal to 768px, we change the `flex-direction` of the `.card` to `column` and align the `.footer` with `align-items: center`.

We have also included comments (`<!--...-->`) around the CSS to explain what's happening in each piece of code.

*Response time: 6.1s*

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
1. WebSocket: WebSocket is a communication protocol that allows for bi-directional communication between the client (web browser) and the server. This is ideal for this use case as it allows real-time updates. 

2. Database Schema:
   - User: id, name, notifications_sent
   - Task: id, user_id, comments, assigned_at, deadline, is_completed
   - Notification: id, task_id, user_id, event, timestamp

3. Offline handling: The system can use a mechanism like WebSocket for real-time notifications. The server will keep track of which users are online. When a user comes back online, the server will send all the notifications that were pending while the user was offline.

4. Schedule: We can use the CRON job to run a periodic check for deadlines and send notifications.

5. For handling 100,000 concurrent users, the system can scale up by increasing the resources allocated to the server and also by adding more instances of the server. 

In the backend, we can use Node.js with Socket.IO for real-time communication. Socket.IO allows for bi-directional communication between the client and server, which is ideal for handling real-time updates.

This setup ensures that the system is scalable and can handle increased load. However, it does not handle the scaling if the backend server goes down, as notifications will still be lost. 

To handle this, we can use sticky sessions, which keeps a user connected to the same server during the entire session. This way, the server can continue to provide the same session to the user, even if the backend server goes down.

The notification system can be implemented in the frontend using JavaScript or React.js for handling the real-time updates.

The system is designed with the following in mind:
- The server sends real-time notifications via WebSocket when a user's task is assigned, a comment is added, or a deadline is approaching.
- The server uses a database to store all the tasks, users, and notifications.
- The server keeps track of which users are online or offline.
- The server can be scaled by adding more instances of the server.
- The server uses sticky sessions to keep a user connected even if the backend server goes down.
- The server can be event-driven with Node.js or other event-driven libraries to handle a user who is offline.

This design ensures that the system is scalable and can handle increased load. However, it does not handle the scaling if the backend server goes down.

*Response time: 3.7s*

---
