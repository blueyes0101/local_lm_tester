# Model: deepseek-coder:1.3b
**Test Date:** 2026-03-10 19:43:34
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
Sure, here's a design of your REST API considering the rules you mentioned.

1. Endpoints:

- GET /workspaces/{workspaceId}/projects
- POST /workspaces/{workspaceId}/projects
- PUT /workspaces/{workspaceId}/projects/{projectId}
- DELETE /workspaces/{workspaceId}/projects/{projectId}
- GET /workspaces/{workspaceId}/projects/{projectId}/tasks
- POST /workspaces/{workspaceId}/projects/{projectId}/tasks
- PUT /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}
- DELETE /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}
- GET /workspaces/{workspaceId}/projects/{projectId}/tasks?assignee={assigneeName}&status={status}&dueDate={dueDate}
- POST /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments
- PUT /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments/{commentId}
- DELETE /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments/{commentId}

2. Error Response:

The error response will be in JSON format. It will contain an error message and a status code. Here is a sample:

```json
{
    "error": "Internal

*Response time: 2.3s*

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
Here's a basic implementation using Node.js, Express, and TypeScript. Note that this implementation does not include the database logic, you will need to integrate it with your application.

Firstly, install the necessary packages:

```bash
npm install --save express zod @types/zod ts-mockito @types/ts-mockito
```

Next, implement the endpoint:

```typescript
import express, { Request, Response, NextFunction } from 'express';
import { ZodError } from 'zod';
import { mock, instance, when } from 'ts-mockito';
import { expect } from 'chai';

import WorkspaceService from '../services/workspace';
import TaskService from '../services/task';

const router = express.Router();

router.patch('/workspaces/:workspaceId/tasks/:taskId', async (req: Request, res: Response, next: NextFunction) => {
  const workspaceId = parseInt(req.params.workspaceId);
  const taskId = parseInt(req.params.taskId);
  const workspaceService = WorkspaceService.getInstance();
  const taskService = TaskService.getInstance();

  // Validate workspaceId and taskId
  if (!workspaceService.workspaceExists(workspaceId)) {
    return res.status(404).send();
  }

  // Validate taskId
  if (!taskService.taskExists(workspaceId, taskId)) {
    return res.status(404).send();
  }

  const patchRequest = {
    title: req.body.title,
    status: req.body.status,
    assignee_id: req.body.assignee_id,
    due_date: req.body.due_date,
  };

  // Validate body using Zod
  const schema = z.object({
    title: z.string().max(200).optional(),
    status: z.union([z.literal('todo'), z.literal('in_progress'), z.literal('done'), z.literal('cancelled')]).optional(),
    assignee_id: z.number().optional(),
    due_date: z.date().optional(),
  });

  try {
    schema.parse(patchRequest);
  } catch (error) {
    if (error instanceof ZodError) {
      return res.status(400).send(error.errors);
    }
    return next(error);
  }

  // Validate assignee_id (if provided)
  if (patchRequest.assignee_id) {
    if (!workspaceService.userExists(patchRequest.assignee_id)) {
      return res.status(400).send('Invalid assignee_id');
    }
  }

  // Validate status to 'cancelled' when task has open subtasks
  const subtasks = taskService.getSubTasks(workspaceId, taskId);
  if (patchRequest.status === 'cancelled' && subtasks.length > 0) {
    return res.status(409).send('Cannot cancel a task with open subtasks');
  }

  // Update task
  try {
    await taskService.updateTask(workspaceId, taskId, patchRequest);
    res.status(200).send('Task updated successfully');
  } catch (error) {
    next(error);
  }
});

export default router;
```

For testing, you can use libraries like Jest and chai:

```typescript
import request from 'supertest';
import chai, { expect } from 'chai';
import chaiHttp from 'chai-http';

import app from '../index';

chai.use(chaiHttp);
chai.use(chai.request(app));

describe('PATCH /workspaces/:workspaceId/tasks/:taskId', () => {
  it('should update a task', async () => {
    // Mock the WorkspaceService
    const workspaceService = mock(WorkspaceService.getInstance());
    when(workspaceService.workspaceExists(1)).thenReturn(true);
    when(workspaceService.userExists(1)).thenReturn(true);
    when(workspaceService.taskExists(1, 1)).thenReturn(true);

    // Mock the TaskService
    const taskService = mock(TaskService.getInstance());
    when(taskService.workspaceExists(1)).thenReturn(true);
    when(taskService.taskExists(1, 1)).thenReturn(true);
    when(taskService.getSubTasks(1, 1)).thenReturn([]);

    const res = await request(app)
      .patch('/workspaces/1/tasks/1')
      .send({
        title: 'New title',
        status: 'todo',
        assignee_id: 1,
        due_date: '2022-01-01',
      });
    expect(res.status).to.equal(200);
    expect(res.body).to.equal('Task updated successfully');
  });

  it('should return 404 if workspace or task does not exist', async () => {
    // Mock the WorkspaceService
    const workspaceService = mock(WorkspaceService.getInstance());
    when(workspaceService.workspaceExists(1)).thenReturn(false);
    when(workspaceService.taskExists(1, 1)).thenReturn(true);

    // Mock the TaskService
    const taskService = mock(TaskService.getInstance());
    when(taskService.workspaceExists(1)).thenReturn(false);
    when(taskService.taskExists(1, 1)).thenReturn(true);

    const res = await request(app).patch('/workspaces/1/tasks/1').send({
      title: 'New title',
      status: 'todo',
      assignee_id: 1,
      due_date: '2022-01-01',
    });
    expect(res.status).to.equal(404);
  });

  it('should return 400 if validation fails', async () => {
    // Mock the WorkspaceService
    const workspaceService = mock(WorkspaceService.getInstance());
    when(workspaceService.workspaceExists(1)).thenReturn(true);
    when(workspaceService.taskExists(1, 1)).thenReturn(true);

    // Mock the TaskService
    const taskService = mock(TaskService.getInstance());
    when(taskService.workspaceExists(1)).thenReturn(true);
    when(taskService.taskExists(1, 1)).thenReturn(true);

    const res = await request(app).patch('/workspaces/1/tasks/1').send({
      status: 'cancelled',
    });
    expect(res.status).to.equal(400);
  });

  it('should return 409 if trying to cancel a task with open subtasks', async () => {
    // Mock the WorkspaceService
    const workspaceService = mock(WorkspaceService.getInstance());
    when(workspaceService.workspaceExists(1)).thenReturn(true);
    when(workspaceService.userExists(1)).thenReturn(true);
    when(workspaceService.taskExists(1, 1)).thenReturn(true);

    // Mock the TaskService
    const taskService = mock(TaskService.getInstance());
    when(taskService.workspaceExists(1)).thenReturn(true);
    when(taskService.taskExists(1, 1)).thenReturn(true);
    when(taskService.getSubTasks(1, 1)).thenReturn([{}]);

    const res = await request(app)
      .patch('/workspaces/1/tasks/1')
      .send({
        status: 'cancelled',
      });
    expect(res.status).to.equal(409);
  });
});
```

In this setup, you have a PATCH endpoint that accepts a PATCH request body with fields to be updated for a task in a workspace. The request body is validated using Zod and the endpoint checks if the workspace and task exist before proceeding with the update. If the update fails due to validation errors, it returns 400. If the workspace or user does not exist, it returns 404. If there are open subtasks and you try to cancel a task with open subtasks, it returns 409. If the update is successful, it returns 200.


*Response time: 12.3s*

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
Here is a simple implementation of the authentication system using Node.js, Express, and TypeScript.

First, install the necessary dependencies:

```bash
npm install express bcrypt jsonwebtoken @types/bcrypt @types/jsonwebtoken express-session
```

Next, define the models:

```typescript
import { Model, model, Schema } from 'mongoose';
import bcrypt from 'bcrypt';

interface IUser {
  email: string;
  password: string;
  role: string;
}

interface IUserDocument extends IUser, Document {}

const UserSchema = new Schema({
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  role: { type: String, required: true },
});

UserSchema.pre('save', async function(this: IUserDocument, next) {
  if (this.isModified('password')) {
    this.password = await bcrypt.hash(this.password, 12);
  }
  next();
});

const User: Model<IUserDocument> = model('User', UserSchema);

export default User;
```

Then, create the authentication middleware:

```typescript
import { Request, Response, NextFunction } from 'express';
import jsonwebtoken from 'jsonwebtoken';
import User from './models/user';

export const authMiddleware = async (req: Request, res: Response, next: NextFunction) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) {
    return res.status(401).json({ message: 'No token provided.' });
  }

  try {
    const decoded = jsonwebtoken.verify(token, process.env.SECRET as string) as { userId: string; iat: number; exp: number };
    const user = await User.findById(decoded.userId);
    if (!user) {
      return res.status(401).json({ message: 'User not found.' });
    }

    req.user = user;
    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ message: 'Token expired.' });
    }
    return res.status(401).json({ message: 'Invalid token.' });
  }
};
```

Finally, create the routes:

```typescript
import { Router } from 'express';
import { createAccessToken, createRefreshToken } from './auth';

const router = Router();

router.post('/auth/register', async (req, res) => {
  const { email, password, role } = req.body;

  const user = new User({ email, password, role });
  await user.save();

  res.json({ user });
});

router.post('/auth/login', async (req, res) => {
  const { email, password } = req.body;

  const user = await User.findOne({ email });
  if (!user) {
    return res.status(401).json({ message: 'User not found.' });
  }

  const isPasswordValid = await bcrypt.compare(password, user.password);
  if (!isPasswordValid) {
    return res.status(401).json({ message: 'Invalid password.' });
  }

  const accessToken = createAccessToken({ userId: user._id });
  const refreshToken = createRefreshToken({ userId: user._id });

  res.cookie('refreshToken', refreshToken, { httpOnly: true, maxAge: 7 * 24 * 60 * 60 * 1000 });
  res.json({ accessToken });
});

router.get('/auth/me', authMiddleware, (req, res) => {
  res.json(req.user);
});

export default router;
```

This is a basic implementation and might need adjustments based on your specific use case. Also, this implementation assumes that you're using MongoDB as your database. In a real-world application, you'd want to use a more secure method of storing refresh tokens, such as a secure, encrypted storage.


*Response time: 5.6s*

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
1. The POST /auth/refresh endpoint uses the refresh token from the cookie to issue a new access token. It also rotates the refresh token, issues a new one, and invalidates the old one.

```python
# Assume you have a function for refreshing the access token
def refresh_token(refresh_token):
    # Refresh token and access token rotation logic here
    access_token = ...
    return access_token

@app.route('/auth/refresh', methods=['POST'])
def refresh_access_token():
    refresh_token = request.cookies.get('refresh_token')
    access_token = refresh_token(refresh_token)
    return jsonify(access_token=access_token)
```

2. The POST /auth/logout endpoint invalidates the refresh token, clears the cookie, and invalidates all the existing sessions.

```python
# Assume you have a function for invalidating a refresh token
def invalidate_refresh_token(refresh_token):
    # Invalidate and clear the refresh token here
    pass

@app.route('/auth/logout', methods=['POST'])
def logout_user():
    refresh_token = request.cookies.get('refresh_token')
    invalidate_refresh_token(refresh_token)
    # Clear the cookie
    response = make_response(jsonify({'message': 'Logged out successfully'}))
    response.delete_cookie('refresh_token')
    return response
```

3. To implement refresh token rotation with a Redis-based token store, you can use a Redis data structure called a 'set' (no two tokens can be in the set at the same time). The TTL (Time To Live) strategy you can use is to automatically delete expired tokens.

4. The case where a refresh token is used twice can be handled by implementing token reuse detection. This can be done by storing the use of a refresh token in a set. If a token is used twice, you can set it in the set and delete it. If it's not used, you can delete it.

```python
# Assume you have a function to check if a refresh token is used
def is_refresh_token_used(refresh_token):
    return refresh_token in redis.smembers('used_refresh_tokens')
```

5. If a user changes their password, you can invalidate ALL their existing sessions by clearing the refresh token in the database.

```python
# Assume you have a function to clear a user's refresh token
def clear_user_refresh_token(user_id):
    # Clear the refresh token in the database here
    pass
```

6. Token blacklisting and token rotation are two different methods of handling expired tokens.

- Token blacklisting: In this method, all tokens are stored in a separate data structure. This is useful when you want to ensure that a token cannot be used again. When a token is used, it is added to the blacklist. If a token is expired or is blacklisted, it cannot be used.

- Token rotation: In this method, a single token is generated and used once. This is useful for generating short-lived, one-time use tokens. The token is generated and used once, and then discarded. This method is useful when you want to generate a token in response to an event, such as a password reset, that is used only once.

In the context of your previous question, if you want to ensure that a token is used only once, use token rotation. If you want to ensure that a token is only used once and can't be used again, use token blacklisting.


*Response time: 4.8s*

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
1. TypeScript Interface for props:
```typescript
interface ColumnProps<T> {
  key: keyof T;
  header: string;
  width?: string;
  sortable?: boolean;
  renderCell?: (rowData: T) => React.ReactNode;
}

interface DataTableProps<T> {
  columns: ColumnProps<T>[];
  data: T[];
}
```

2. The complete component implementation:
```typescript
import React from 'react';
import { useTable, usePagination, useSortBy, useFilters } from 'react-table';

const DataTable: React.FC<DataTableProps<any>> = ({ columns, data }) => {
  // Use the state and functions returned from useTable to build your UI.
  const defaultColumn = React.useMemo(() => columns[0], [columns]);
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
  } = useTable({ columns, data }, usePagination, useSortBy, useFilters);

  // Render the UI for your table
  return (
    <table {...getTableProps()}>
      <thead>
        <tr {...headerGroups[0].getHeaderGroupProps()}>
          {headerGroups[0].headers.map(column => (
            <th
              {...column.getHeaderProps(column.getSortByToggleProps())
                .filter(prop => prop.name === 'sort')}
              style={{
                width: column.width,
                ...(column.headerStyle || {})
              }}
            >
              {column.render('Header')}
              {column.isSorted
                ? column.isSortedDesc
                  ? ' 🔽'
                  : ' 🔼'
                : ''}
            </th>
          ))}
        </tr>
      </thead>
      <tbody {...getTableBodyProps()}>
        {rows.map(row => {
          prepareRow(row);
          return (
            <tr {...row.getRowProps()}>
              {row.cells.map(cell => {
                return (
                  <td {...cell.getCellProps()}>
                    {React.isValidElement(cell.value)
                      ? cell.render('Cell')
                      : cell.value}
                  </td>
                );
              })}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};
```

3. Usage example with 3 columns:
```typescript
const data = useMemo(() => generateData(1000), []);

const columns = useMemo(
  () => [
    {
      Header: 'Name',
      accessor: 'name', // accessor is the "key" a associated with a particular row-data.
      width: '30%',
    },
    {
      Header: 'Country',
      accessor: 'country',
      width: '30%',
    },
    {
      Header: 'Action',
      accessor: 'action',
      width: '40%',
      renderCell: (rowData: any) => (
        <button onClick={() => handleDelete(rowData.id)}>Delete</button>
      ),
    },
  ],
  []
);

return <DataTable columns={columns} data={data} />;
```

4. How to memoize this correctly?
The most suitable way to memoize is by using the memo function provided by React and its hooks. This will ensure that the DataTable component will only re-render when the props of the component change. In the provided code, we are using memoization on the DataTable component itself and then on the columns array.

```typescript
const DataTable = React.memo(styledTable => {
  // ...rest of your component
});
```

You can use this memoization to avoid unnecessary re-renders in your component. However, you should be careful when using memoization with components that have child components that use hooks. If you do not memoize the entire component, you might end up with an infinite loop of unnecessary re-renders. In such cases, you should use a technique called "should component update" or use a custom shouldComponentUpdate hook.


*Response time: 6.0s*

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
1. Custom Hook `useSearch`:

```javascript
import { useState, useEffect } from 'react';
import { useHistory, useLocation } from 'react-router-dom';

const useSearch = (query) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [cache, setCache] = useState(null);
  const [debouncedQuery, setDebouncedQuery] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const history = useHistory();
  const location = useLocation();

  useEffect(() => {
    if (!query) return;
    setDebouncedQuery(query);

    const timer = setTimeout(() => {
      setLoading(true);
      setError(false);
      fetchResults();
    }, 300);

    return () => {
      clearTimeout(timer);
    };
  }, [query]);

  useEffect(() => {
    if (!debouncedQuery) return;
    setIsSearching(true);
    fetch(`/api/search?q=${debouncedQuery}`)
      .then((res) => {
        if (res.ok) {
          setLoading(false);
          setIsSearching(false);
          setResults(await res.json());
          setCache(results);
          localStorage.setItem(`searchterm_${debouncedQuery}`, JSON.stringify(results));
          setTimeout(() => {
            localStorage.removeItem(`searchterm_${debouncedQuery}`);
          }, 300000);
        } else {
          setError(true);
          setLoading(false);
        }
      })
      .catch((err) => {
        setError(true);
        setLoading(false);
      });
  }, [debouncedQuery]);

  useEffect(() => {
    if (!cache) return;
    if (localStorage.getItem(`searchterm_${query}`)) {
      setResults(JSON.parse(localStorage.getItem(`searchterm_${query}`)));
      setLoading(false);
    }
  }, [query, cache]);

  useEffect(() => {
    if (!results) return;
    if (!results.length) {
      setError("No results");
    }
  }, [results]);

  const fetchResults = () => {
    if (isSearching) return;
    history.push(`/search?q=${debouncedQuery}`);
  };

  return { loading, error, results };
};

export default useSearch;
```

2. The `SearchPage` component using `useSearch` hook:

```javascript
import React, { useState } from 'react';
import useSearch from './useSearch';

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const { loading, error, results } = useSearch(query);

  return (
    <div>
      <input type="text" onChange={(e) => setQuery(e.target.value)} />
      {loading && <div>Loading...</div>}
      {error && <div>Error, please retry</div>}
      {results && !loading && !error && (
        <div>
          {results.map((item, index) => (
            <div key={index}>{item}</div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchPage;
```

3. URL Sync Implementation:

In order to sync URL, we can use the `useLocation` hook in React Router. Whenever the `query` state changes, we will update the URL accordingly.

4. Cancelling In-flight Requests:

Cancelling in-flight requests is important because it allows us to prevent multiple requests to the API at the same time. If a new search is started before the previous one is completed, the old request will not be cancelled. This prevents potential issues such as multiple requests at the same time or too many requests at once.

Bug prevention: Cancelling in-flight requests prevents the old request from completing, which could potentially result in data being fetched from an old request. It also prevents unnecessary API calls when a user types within 300ms of the old request, which could lead to unnecessary API calls.


*Response time: 6.2s*

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
1. Prisma query:
```prisma
model User {
  id        Int       @id @default(autoincrement())
  email     String    @unique
  posts     Post[]
}

model Post {
  id        Int       @id @default(autoincrement())
  title     String
  content   String
  published Boolean   @default(false)
  authorId  Int
  author    User      @relation(fields: [authorId], link: [id])
  tags      Tag[]
  comments  Comment[]
  createdAt DateTime  @default(now())
}

model Tag {
  id    Int    @id @default(autoincrement())
  name  String @unique
  posts Post[]
}

model Comment {
  id        Int      @id @default(autoincrement())
  content   String
  postId    Int
  post      Post     @relation(fields: [postId], link: [id])
  authorId  Int
  author    User     @relation(fields: [authorId], link: [id])
  createdAt DateTime @default(now())
}

// Fetch 10 most recent published posts, including author name, tag names, and comment count
query {
  posts(
    where: { published: true },
    orderBy: [createdAt_DESC()],
    include: {
      author: { select: { name: true } },
      tags: { select: { name: true } },
      comments: { select: { count: true } }
    }
  ) {
    id
    title
    content
    author { select: { name: true } }
    tags { select: { name: true } }
    comments { select: { count: true } }
  }
}
```
2. Migration scenario to add slug field to Post:
```prisma
model {
  name: String
  slug: String @unique
}

model Post {
  id        Int @id @default(autoincrement())
  title     String
  content   String
  published Boolean @default(false)
  authorId  Int
  author    User @relation(fields: [authorId], link: [id])
  tags      Tag[]
  comments  Comment[]
  createdAt DateTime @default(now())
  slug      String @map("slugGenerator")
}

generator slugGenerator {
  model {
    name
    title
  }
  provider "prisma-slug-generator" {
    field "name"
    field "title"
  }
}
```
3. Slow Prisma query:
```prisma
query {
  posts(
    where: { tags: { name: "tagName" } },
    orderBy: [createdAt_DESC()],
    include: {
      author: { select: { name: true } },
      tags: { select: { name: true } },
      comments: { select: { count: true } }
    }
  ) {
    id
    title
    content
    author { select: { name: true } }
    tags { select: { name: true } }
    comments { select: { count: true } }
  }
}
```
The slow query is generated by Prisma because the `posts` relation is specified in the `include` section, meaning Prisma will load all the related data together in one query. This can lead to a performance hit.

To fix this, we can move the `tags` and `comments` selects to the `where` clause of the `posts` relation:

```prisma
query {
  posts(
    where: { tags: { name: "tagName" } },
    orderBy: [createdAt_DESC()],
    include: {
      author: { select: { name: true } },
      comments: { select: { count: true } }
    }
  ) {
    id
    title
    content
    author { select: { name: true } }
    comments { select: { count: true } }
  }
}
```

4. When the performance becomes slow, Prisma would switch to raw SQL to fetch the data. This is when the query is slow, and Prisma has to generate the raw SQL query to fetch data. When the performance is slow, Prisma switches to raw SQL to fetch the data. This can be useful when you want to add a new field to the model or a new relation, but you don't want to break the application. You can then switch back to Prisma to perform updates.


*Response time: 6.0s*

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
1. docker-compose.yml

```yaml
version: '3'
services:
  web:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    volumes:
      - ./frontend:/app
      - ./node_modules:/app/node_modules
    ports:
      - 3000:3000
    depends_on:
      - db
    environment:
      - NODE_ENV=development
    restart: on-failure
  db:
    image: postgres:latest
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=database
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
  redis:
    image: redis:latest
    ports:
      - 6379:6379
```

2. Dockerfile for the backend Node.js

```Dockerfile
# Use an official Node.js runtime as the parent image
FROM node:14

# Set the working directory in the container to /app
WORKDIR /app

# Copy package.json and package-lock.json around the code to create a consistent working directory
COPY package*.json ./

# Install all the dependencies
RUN npm install

# Bundle app source
COPY . .

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NODE_ENV=development

# Define a default command to run the app
CMD [ "node", "server.js" ]
```

3. The backend crashes in production with exit code 137 means that Node.js process got an unhandled promise rejection. This usually means that the app has encountered an error and is now exiting. To diagnose this, you need to check the logs of the Node.js process.

4. Deploying a new version with zero downtime:

1. Stop all instances of the service.

2. Pull the latest version of the backend service from the version control system (like Git).

3. Update the database schema. You can use migrations in the database to keep track of changes to the schema.

4. Update the code. Push the changes to the version control system (Git).

5. Update the Docker image. Build a new Docker image for the updated service and use it to replace the old one.

6. Update the service in Kubernetes. Kubernetes handles the rolling updates for you.

7. Start all instances of the updated service.

8. Remove all instances of the old service.

Remember to keep your docker-compose.yml updated as the services and their dependencies can change over time.


*Response time: 3.9s*

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
Here is a simple implementation of a WebSocket server using Node.js with the ws library.

```javascript
const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

let connections = new Map();

wss.on('connection', ws => {
  const userId = 'user' + Math.random();
  connections.set(ws, userId);
  ws.on('message', message => {
    const { type, payload } = JSON.parse(message.toString());
    if (type === 'join') {
      const userId = connections.get(ws);
      wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN && client !== ws) {
          client.send(JSON.stringify({ type: 'textChange', payload: { userId, text: payload.text } }));
        }
      });
    } else if (type === 'cursorMove') {
      const userId = connections.get(ws);
      wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN && client !== ws) {
          client.send(JSON.stringify({ type: 'cursorMove', payload: { userId, cursor: payload.cursor } }));
        }
      });
    } else if (type === 'userLeft') {
      const userId = connections.get(ws);
      connections.delete(ws);
      wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify({ type: 'userLeft', payload: { userId } }));
        }
      });
    }
  });
});
```

This server handles multiple connections and broadcasts updates to all connected clients, even if a user reconnects.

When a user leaves, the server sends a 'userLeft' message to all other users in the same document. When a user reconnects, the server sends a 'join' message to all other users in the same document.

Two users editing the same position simultaneously can result in data inconsistency. This is because they are not only modifying the same data (they're modifying the document), but they're also modifying the same part of the data (they're modifying the cursor). This will cause a conflict and require a more complex solution. One approach is to use a combination of the user's ID and the time it was modified, to ensure that only one user can edit a position at a time. However, this requires a more complex solution to implement, as it introduces an additional, complex layer of concurrency control.

In this simplified example, if two users are editing the exact same position simultaneously, the server will not send a 'textChange' or 'cursorMove' message to the other user.


*Response time: 3.9s*

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
1. GraphQL Schema (SDL):
```graphql
scalar Date

type Recipe {
  id: ID!
  title: String!
  author: User!
  tags: [String!]!
  ingredients: [Ingredient!]!
  steps: [String!]!
  ratings: [Rating!]!
}

type User {
  id: ID!
  name: String!
  recipes: [Recipe!]!
}

type Ingredient {
  id: ID!
  name: String!
  amount: Float!
  unit: String!
}

type Rating {
  id: ID!
  score: Float!
  comment: String!
  recipe: Recipe!
}

input RecipeFilter {
  tag: String
  minRating: Float
}

input Pagination {
  page: Int
  limit: Int
}

type Query {
  recipes(filter: RecipeFilter, pagination: Pagination): [Recipe!]
  recipe(id: ID!): Recipe
  recipeAverageRating(id: ID!): Float
}

type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String): Rating!
}
```
2. Resolvers for the query:
```javascript
Recipe: {
  author: (parent, args, context, info) => context.dataSources.userAPI.getUserById(parent.author),
  ingredients: (parent, args, context, info) => context.dataSources.ingredientAPI.getIngredientsByRecipeId(parent.id),
  ratings: (parent, args, context, info) => context.dataSources.ratingAPI.getRatingsByRecipeId(parent.id)
}

Rating: {
  recipe: (parent, args, context, info) => context.dataSources.recipeAPI.getRecipeById(parent.recipe)
}

Query: {
  recipes: (parent, args, context, info) => context.dataSources.recipeAPI.getRecipes(args.filter, args.pagination),
  recipe: (parent, args, context, info) => context.dataSources.recipeAPI.getRecipeById(args.id),
  recipeAverageRating: (parent, args, context, info) => context.dataSources.recipeAPI.getAverageRating(args.id)
}

Mutation: {
  addRating: (parent, args

*Response time: 3.4s*

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
Here is a simple implementation of the requested layout using HTML and CSS:

HTML:
```html
<div class="container">
  <div class="header">
    <!-- Header content -->
  </div>
  <div class="content">
    <div class="sidebar">
      <!-- Sidebar content -->
    </div>
    <div class="main-content">
      <!-- Main content -->
    </div>
  </div>
</div>
```

CSS:
```css
.container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.header {
  position: fixed;
  height: 60px;
  /* Other styles here */
}

.content {
  display: flex;
  flex: 1;
}

.sidebar {
  width: 240px;
  overflow: auto;
  /* Other styles here */
}

.main-content {
  flex: 1;
  overflow: auto;
  /* Other styles here */
}

.card {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-gap: 20px;
  /* Other styles here */
}

.button {
  /* Other styles here */
}

@media (max-width: 768px) {
  .container {
    flex-direction: column;
  }

  .content {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
  }

  .main-content {
    width: 100%;
  }

  .card {
    grid-template-columns: 1fr;
  }
}
```

Explanation:

1. `display: flex;` on the `.container` and `.content` will create a flex container, and its children will inherit this property.

2. `.header` is set to `position: fixed;`, which makes it stick to the top of the page.

3. `.content` is set to `display: flex;`, which will make it a flex container and the child elements will inherit this property.

4. `.sidebar` and `.main-content` are set to `width: 240px;` and `overflow: auto;`, respectively. This ensures that they will scroll independently.

5. `.card` is set to `display: grid;` and `grid-template-columns: 1fr 1fr;`, which will create a responsive grid with 2 columns for desktops and 1 column for mobile devices.

6. `@media (max-width: 768px)` is a media query that will apply styles for screens that are 768px or less. This means that the layout will switch to a vertical mode for screens that are less than 768px wide.

Note: You'll need to add the relevant styles to the HTML and CSS to create the desired layout.


*Response time: 4.2s*

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
1. Transport mechanism:
   The real-time notification system would be designed using a WebSocket transport mechanism as it provides a low-latency and bidirectional communication between the client and the server. It can handle multiple simultaneous connections and messages. In addition, the use of WebSockets allows for the real-time exchange of data, without the need for a round trip from the server to the client.

2. Database schema:
   For storing notifications, a relational database like MySQL or PostgreSQL could be used. The schema would involve the following tables:

   - Users: UserId, Username, Email, etc.
   - Tasks: TaskId, Title, AssignedUserId, etc.
   - Comments: CommentId, TaskId, UserId, CommentText, etc.
   - Notifications: NotificationId, UserId, TaskId, CommentId, Type (assigned, comment, deadline), Timestamp.

3. Handling offline users:
   To handle offline users, a client-side solution would be required. This can be achieved using a service worker in the browser. The service worker maintains a open connection with the server and listens for updates. When a user comes back online, the service worker can send a message to the server to mark the notification as read.

4. Deadline check:
   This could be implemented using a cron job. The cron job can be set up to run at specific intervals (every hour for tasks), and it would send a message to the server with the task details. The server can then process the tasks and send notifications.

5. Scaling:
   If there are 100,000 concurrent users, a horizontally scalable approach could be used. This means that more instances of the notification service can be run in parallel. This is because the service workers can still handle multiple connections, and the load can be distributed across the instances. Also, the notification service can be stateless, so it can handle a large number of simultaneous connections and messages with minimal impact on the server's resources.


*Response time: 2.4s*

---
