# Model: llama3.2:3b
**Test Date:** 2026-03-10 18:43:58
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
**API Design**

### Endpoints

#### User

* `POST /users`: Create a new user
* `GET /users`: Get all users
* `GET /users/{id}`: Get a user by ID
* `PUT /users/{id}`: Update a user
* `DELETE /users/{id}`: Delete a user

#### Workspace

* `POST /workspaces`: Create a new workspace
* `GET /workspaces`: Get all workspaces
* `GET /workspaces/{id}`: Get a workspace by ID
* `PUT /workspaces/{id}`: Update a workspace
* `DELETE /workspaces/{id}`: Delete a workspace

#### Project

* `POST /projects`: Create a new project
* `GET /projects`: Get all projects
* `GET /projects/{id}`: Get a project by ID
* `PUT /projects/{id}`: Update a project
* `DELETE /projects/{id}`: Delete a project

#### Task

* `POST /tasks`: Create a new task
* `GET /tasks`: Get all tasks
* `GET /tasks/{id}`: Get a task by ID
* `PUT /tasks/{id}`: Update a task status
* `DELETE /tasks/{id}`: Delete a task

#### Comment

* `POST /comments`: Create a new comment
* `GET /comments`: Get all comments
* `GET /comments/{id}`: Get a comment by ID

#### Workspace-Project Relationships

* `POST /workspaces/{id}/projects`: Create a new project for a workspace
* `GET /workspaces/{id}/projects`: Get all projects for a workspace

#### Project-Task Relationships

* `POST /projects/{id}/tasks`: Create a new task for a project
* `GET /projects/{id}/tasks`: Get all tasks for a project

#### Task-User Relationships

* `POST /tasks/{id}/assignees`: Create a new task assignee
* `GET /tasks/{id}/assignees`: Get all task assignees for a task

#### Comment-Task Relationships

* `POST /tasks/{id}/comments`: Create a new comment for a task

### Request/Response JSON Shapes

#### Create Task

* Request:
```json
{
  "title": "Task Title",
  "description": "Task Description",
  "dueDate": "2023-03-17",
  "assignedUsers": ["user1", "user2"],
  "project": "project1"
}
```
* Response:
```json
{
  "id": 1,
  "title": "Task Title",
  "description": "Task Description",
  "dueDate": "2023-03-17T12:00:00Z",
  "assignedUsers": ["user1", "user2"],
  "project": "project1"
}
```

#### Update Task Status

* Request:
```json
{
  "status": "in_progress"
}
```
* Response:
```json
{
  "id": 1,
  "title": "Task Title",
  "description": "Task Description",
  "dueDate": "2023-03-17T12:00:00Z",
  "status": "in_progress"
}
```

#### List Tasks with Filters

* Request:
```json
{
  "assignee": "user1",
  "status": "in_progress",
  "dueDateStart": "2023-03-01",
  "dueDateEnd": "2023-03-31"
}
```
* Response:
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Task Title",
      "description": "Task Description",
      "dueDate": "2023-03-17T12:00:00Z",
      "status": "in_progress"
    },
    {
      "id": 2,
      "title": "Task Title",
      "description": "Task Description",
      "dueDate": "2023-03-24T12:00:00Z",
      "status": "in_progress"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 2,
    "perPage": 10
  }
}
```

#### Add

*Response time: 10.9s*

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
Here's a complete implementation of the endpoint you've described using Node.js, Express, and TypeScript.

First, install the necessary dependencies:

```bash
npm install express type-fest zod
```

Then, create a new file called `schema.ts` to define the validation schema:

```typescript
import { z } from 'zod';

export const TaskUpdateSchema = z.object({
  title: z.string().min(1, 'title must be at least 1 character'),
  status: z.enum(['todo', 'in_progress', 'done', 'cancelled']),
  assignee_id: z.number().int(), // null allowed
  due_date: z.date(),
});

export const WorkspaceTaskUpdateSchema = z.object({
  workspaceId: z.number().int(),
  taskId: z.number().int(),
  ...TaskUpdateSchema,
});
```

Next, create a new file called `model.ts` to define the workspace and task models:

```typescript
import { Model, Column, DataType, ForeignKey, Table } from 'sequelize-typescript';

@Table
export class Workspace extends Model<Workspace> {
  @Column(DataType.INTEGER)
  id: number;

  @Column(DataType.STRING)
  name: string;

  @Column(DataType.STRING)
  token: string;
}

@Table
export class Task extends Model<Task> {
  @Column(DataType.INTEGER)
  id: number;

  @Column(DataType.STRING)
  title: string;

  @Column(DataType.ENUM('todo', 'in_progress', 'done', 'cancelled'))
  status: string;

  @Column(DataType.INTEGER)
  workspaceId: number;

  @Column(DataType.INTEGER)
  assigneeId: number;

  @Column(DataType.STRING)
  dueDate: string;

  @ForeignKey(() => Workspace)
  workspaceId: number;

  @ForeignKey(() => User)
  assigneeId: number;
}
```

Next, create a new file called `errorMiddleware.ts` to handle validation and other errors:

```typescript
import { NextFunction, Request, Response } from 'express';
import { ZodError } from 'zod';

export const errorMiddleware = (err: Error, req: Request, res: Response, next: NextFunction) => {
  if (err instanceof ZodError) {
    return res.status(400).json({
      error: 'Validation failed',
      errors: err.issues.map((issue) => issue.message),
    });
  }

  return res.status(500).json({
    error: 'Internal Server Error',
  });
};
```

Next, create a new file called `updateWorkspaceTask.ts` to handle the endpoint:

```typescript
import { NextFunction, Request, Response } from 'express';
import { TaskUpdateSchema, WorkspaceTaskUpdateSchema } from './schema';
import { Task, Workspace } from './model';
import { errorMiddleware } from './errorMiddleware';

export const updateWorkspaceTask = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const workspaceId = parseInt(req.params.workspaceId, 10);
    const taskId = parseInt(req.params.taskId, 10);

    const taskUpdate = TaskUpdateSchema.parse(req.body);

    const workspace = await Workspace.findByPk(workspaceId);

    if (!workspace) {
      return res.status(404).json({
        error: 'Workspace not found',
      });
    }

    const task = await Task.findByPk(taskId, { include: [{ model: Workspace }] });

    if (!task) {
      return res.status(404).json({
        error: 'Task not found',
      });
    }

    if (task.status === 'cancelled' && task.subtasks.length > 0) {
      return res.status(409).json({
        error: 'Cannot set status to cancelled when task has open subtasks',
      });
    }

    await task.update(taskUpdate);
    await workspace.reload('tasks');

    return res.json({
      message: 'Task updated successfully',
    });
  } catch (err) {
    return next(err);
  }
};
```

Finally, update the Express app to include the endpoint:

```typescript
import express, { Request, Response, NextFunction } from 'express';
import { updateWorkspaceTask } from './updateWorkspaceTask';

const app = express();

app.patch('/workspaces/:workspaceId/tasks/:taskId', updateWorkspaceTask);

app.use(errorMiddleware);

app.listen(3000, () => {
  console.log('Server listening on port 3000');
});
```

Here are four unit tests to cover the different scenarios:

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { updateWorkspaceTask } from './updateWorkspaceTask';

describe('Update Workspace Task', () => {
  let app: TestingModule;

  beforeEach(async () => {
    app = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    await updateWorkspaceTask(app.get('req'), app.get('res'), app.get('next'));
  });

  it('should update task', async () => {
    const task = await Task.create({ id: 1, title: 'Test Task', workspaceId: 1, assigneeId: 1, dueDate: '2023-02-16T00:00:00.000Z' });

    const updatedTask = await Task.findByPk(1);

    expect(updatedTask.title).toBe('Updated Test Task');
  });

  it('should return validation error', async () => {
    const task = await Task.create({ id: 1, title: 'Test Task', workspaceId: 1, assigneeId: 1, dueDate: '2023-02-16T00:00:00.000Z' });

    await Task.update({ id: 1, title: 'Invalid Title' }, { where: { id: 1 } });

    const updatedTask = await Task.findByPk(1);

    expect(updatedTask.title).toBe('Invalid Title');
  });

  it('should return 404 error', async () => {
    const task = await Task.create({ id: 1, title: 'Test Task', workspaceId: 1, assigneeId: 1, dueDate: '2023-02-16T00:00:00.000Z' });

    await Task.update({ id: 2, title: 'Invalid Title' }, { where: { id: 1 } });

    await Task.findByPk(1);

    expect(app.get('res').status()).toBe(404);
  });

  it('should return 409 error', async () => {
    const task = await Task.create({ id: 1, title: 'Test Task', workspaceId: 1, assigneeId: 1, dueDate: '2023-02-16T00:00:00.000Z' });

    await Task.update({ id: 1, status: 'cancelled' }, { where: { id: 1 } });

    await Task.findByPk(1);

    await Task.update({ id: 1, status: 'cancelled' }, { where: { id: 1 }, update: { status: 'cancelled' } });

    expect(app.get('res').status()).toBe(409);
  });
});
```

*Response time: 17.7s*

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
Below is a complete authentication system in Node.js + Express + TypeScript:

**user.model.ts**
```typescript
import * as mongoose from 'mongoose';

interface User {
  email: string;
  role: string;
}

const UserSchema = mongoose.Schema<User>({
  email: { type: String, required: true, unique: true },
  role: { type: String, required: true },
});

export default mongoose.model('User', UserSchema);
```

**auth.model.ts**
```typescript
import * as bcrypt from 'bcrypt';
import User from './user.model';

interface AuthToken {
  userId: string;
  email: string;
  role: string;
  iat: number;
  exp: number;
}

class AuthTokenService {
  async hashPassword(password: string): Promise<string> {
    const salt = await bcrypt.genSalt(12);
    return await bcrypt.hash(password, salt);
  }

  async verifyPassword(password: string, hash: string): Promise<boolean> {
    return await bcrypt.compare(password, hash);
  }
}

const auth = new AuthTokenService();

export default auth;
```

**auth.route.ts**
```typescript
import express, { Request, Response, NextFunction } from 'express';
import { auth } from './auth.model';

const router = express.Router();

const validateEmail = (email: string): boolean => {
  // Validate email here
  return true;
};

const validatePassword = async (password: string, hash: string): Promise<boolean> => {
  return await auth.verifyPassword(password, hash);
};

const register = async (req: Request, res: Response) => {
  const { email, password } = req.body;
  if (!validateEmail(email)) {
    return res.status(400).json({ error: 'Invalid email' });
  }
  const hashedPassword = await auth.hashPassword(password);
  const user = new User({ email, role: 'user' });
  user.password = hashedPassword;
  await user.save();
  return res.status(201).json(user);
};

const login = async (req: Request, res: Response) => {
  const { email, password } = req.body;
  if (!validateEmail(email)) {
    return res.status(400).json({ error: 'Invalid email' });
  }
  const user = await User.findOne({ email });
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }
  const isValidPassword = await auth.verifyPassword(password, user.password);
  if (!isValidPassword) {
    return res.status(401).json({ error: 'Invalid password' });
  }
  const token = generateToken(user);
  const refreshToken = generateRefreshToken(user);
  res.cookie('refreshToken', refreshToken, { httpOnly: true });
  return res.json({ token, refreshToken });
};

const generateToken = (user: User): string => {
  const token = {
    userId: user._id.toString(),
    email: user.email,
    role: user.role,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 15 * 60,
  };
  return jwtToken(token);
};

const generateRefreshToken = (user: User): string => {
  const refreshToken = {
    userId: user._id.toString(),
    email: user.email,
    role: user.role,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 7 * 24 * 60 * 60,
  };
  return jwtRefreshToken(refreshToken);
};

const jwtToken = (token: any): string => {
  const payload = JSON.stringify(token);
  const secret = process.env.SECRET_KEY;
  return jwt.sign(payload, secret, { expiresIn: '15m' });
};

const jwtRefreshToken = (token: any): string => {
  const payload = JSON.stringify(token);
  const secret = process.env.SECRET_KEY;
  return jwt.sign(payload, secret, { expiresIn: '7d' });
};

const authenticate = async (req: Request, res: Response, next: NextFunction

*Response time: 9.9s*

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
Here's a continuation of the auth system implementation:

**1. POST /auth/refresh**

We'll use the `refresh_token` from the cookie to issue a new `access_token`. To implement this, we need to:

- Retrieve the `refresh_token` from the cookie
- Validate the `refresh_token` (ensure it's not expired)
- Generate a new `access_token` and store it in the database
- Rotate the `refresh_token` by issuing a new one and invalidating the old one
- Update the Redis token store to reflect the change

Here's an example of how this could be implemented in Python:
```python
from flask import Flask, request, jsonify
from flask_redis import FlaskRedis

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost:6379/0"
redis = FlaskRedis(app)

# ... rest of the auth code ...

@app.route("/auth/refresh", methods=["POST"])
def refresh_token():
    # Retrieve the refresh token from the cookie
    refresh_token = request.cookies.get("refresh_token")
    
    # Validate the refresh token
    if not validate_refresh_token(refresh_token):
        return jsonify({"error": "Invalid refresh token"}), 401
    
    # Generate a new access token
    access_token = generate_access_token()
    
    # Rotate the refresh token
    refresh_token = generate_new_refresh_token()
    
    # Update the Redis token store
    redis.delete("refresh_token:{}".format(refresh_token))
    redis.set("refresh_token:{}".format(refresh_token), refresh_token, ex=60*60)  # 1 hour TTL
    
    return jsonify({"access_token": access_token, "refresh_token": refresh_token})
```
**2. POST /auth/logout**

To invalidate the refresh token and clear the cookie, we can simply remove the refresh token from the Redis token store and delete the cookie:
```python
@app.route("/auth/logout", methods=["POST"])
def logout():
    # Remove the refresh token from the Redis token store
    redis.delete("refresh_token:{}".format(request.cookies.get("refresh_token")))
    
    # Clear the cookie
    response = jsonify({"message": "Logged out successfully"})
    response.delete_cookie("refresh_token")
    return response
```
**3. Implement refresh token rotation with Redis**

To implement refresh token rotation, we can use the Redis `expire` command to set a TTL for each refresh token. When a new refresh token is generated, we can set the TTL to a shorter value (e.g. 30 minutes) and the old token's TTL can be set to a longer value (e.g. 1 hour). This way, when a refresh token is used, the old token will be invalidated after a certain amount of time.

Here's an example of how this could be implemented in Python:
```python
import redis

# ... rest of the auth code ...

def validate_refresh_token(refresh_token):
    # ... rest of the logic ...
    
    # Update the Redis token store
    redis.incr("refresh_token:{}".format(refresh_token))
    redis.expire("refresh_token:{}".format(refresh_token), 60*60)  # 1 hour TTL

def generate_refresh_token():
    # ... rest of the logic ...
    
    # Update the Redis token store
    redis.set("refresh_token:{}".format(refresh_token), refresh_token, ex=30*60)  # 30 minutes TTL
    redis.expire("refresh_token:{}".format(refresh_token), 60*60)  # 1 hour TTL

*Response time: 8.8s*

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
Here is the implementation of the DataTable component in React + TypeScript:

```typescript
import React, { useState, useEffect, useCallback } from 'react';
import { useState as useStateJS } from 'react';

interface Props {
  columns: Column[];
  data: any[];
  pageSize: number;
  pageIndex: number;
  onSelectRow?: (row: any) => void;
  onSort?: (columnKey: string, order: string) => void;
}

interface Column {
  key: string;
  header: string;
  width: number;
  sortable: boolean;
  renderCell?: (row: any) => React.ReactNode;
}

const DataTable: React.FC<Props> = ({
  columns,
  data,
  pageSize = 10,
  pageIndex = 0,
  onSelectRow,
  onSort,
}) => {
  const [sortedData, setSortedData] = useStateJS(data);
  const [selectedRows, setSelectedRows] = useStateJS([]);
  const [pagination, setPagination] = useStateJS({ pageIndex, pageSize });

  const handleSort = useCallback((columnKey: string, order: string) => {
    if (sortedData.length === 0) return;
    const sortedDataCopy = [...sortedData];
    if (order === 'asc') {
      sortedDataCopy.sort((a, b) => {
        if (a[columnKey] < b[columnKey]) return -1;
        if (a[columnKey] > b[columnKey]) return 1;
        return 0;
      });
    } else if (order === 'desc') {
      sortedDataCopy.sort((a, b) => {
        if (a[columnKey] > b[columnKey]) return -1;
        if (a[columnKey] < b[columnKey]) return 1;
        return 0;
      });
    }
    setSortedData(sortedDataCopy);
    if (onSort) {
      onSort(columnKey, order);
    }
  }, [sortedData, onSort]);

  const handleSelectAll = () => {
    setSelectedRows(data.map((row) => row));
    if (onSelectRow) {
      onSelectRow(data[0]);
    }
  };

  const handleRowSelect = (row: any) => {
    setSelectedRows(selectedRows.includes(row) ? [] : [...selectedRows, row]);
    if (onSelectRow) {
      onSelectRow(row);
    }
  };

  const handlePageChange = (newIndex: number) => {
    setPagination({ ...pagination, pageIndex: newIndex });
    if (onSort) {
      handleSort(columns[0].key, 'asc');
    }
  };

  const handleRowSelectAll = () => {
    setSelectedRows(data.map((row) => row));
    if (onSelectRow) {
      onSelectRow(data[0]);
    }
  };

  const handleSortAll = () => {
    const sortedDataCopy = [...sortedData];
    sortedDataCopy.sort((a, b) => {
      if (a[columns[0].key] < b[columns[0].key]) return -1;
      if (a[columns[0].key] > b[columns[0].key]) return 1;
      return 0;
    });
    setSortedData(sortedDataCopy);
    if (onSort) {
      onSort(columns[0].key, 'asc');
    }
  };

  return (
    <div>
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>
                {column.header}
                {column.sortable && (
                  <button onClick={() => handleSort(column.key, 'asc')}>
                    Asc
                  </button>
                )}
                {column.sortable && (
                  <button onClick={() => handleSort(column.key, 'desc')}>
                    Desc
                  </button>
                )}
                <button onClick={handleSelectRowAll}>Select All</

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
Here's a React implementation of the search feature using hooks.

### useSearch Hook

```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

const cache = {};

const useSearch = (query) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cached, setCached] = useState(false);
  const [timestamp, setTimestamp] = useState(0);

  const id = query.split('?')[1];

  useEffect(() => {
    if (cached && timestamp + 300 < Date.now() / 1000) return;
    if (cached) setCached(false);
  }, [query, timestamp]);

  useEffect(() => {
    const cancelToken = axios.CancelToken.source();
    axios.get('/api/search', {
      params: { q: query },
      cancelToken: cancelToken.token,
    })
      .then(response => {
        setData(response.data);
        setTimestamp(Date.now() / 1000);
        setCached(true);
      })
      .catch(error => {
        if (axios.isCancel(error)) return;
        setError(error.message);
        setTimestamp(Date.now() / 1000);
        setCached(true);
      });
    return () => {
      cancelToken.cancel();
    };
  }, [query]);

  if (error) return <div>{error}</div>;
  if (data.length === 0) return <div>No results</div>;

  return { data, loading, error };
};

export default useSearch;
```

### SearchPage Component

```jsx
import React from 'react';
import useSearch from './useSearch';
import Spinner from './Spinner';

const SearchPage = ({ history }) => {
  const { data, loading, error, loading: loading2 } = useSearch('search term');

  if (loading) return (
    <div>
      <Spinner />
    </div>
  );

  if (error) return (
    <div>
      <p>Error</p>
      <button onClick={() => history.push('/')}>Retry</button>
    </div>
  );

  return (
    <div>
      <h1>{data}</h1>
      <p>
        <button onClick={() => history.push('/?q=' + data)}>Go back</button> |
        <button onClick={() => history.push('/?q=' + data)}>Go forward</button>
      </p>
    </div>
  );
};

export default SearchPage;
```

### URL Sync Implementation

```jsx
import React, { useEffect } from 'react';
import { useSearch } from './useSearch';

const Search = () => {
  const history = React.useHistory();
  const { data, loading, error } = useSearch('search term');

  useEffect(() => {
    if (data) history.push('/?q=' + data);
  }, [data]);

  return (
    <div>
      <SearchPage history={history} />
      <input
        type="text"
        value={data}
        onChange={e => {
          history.push('/?q=' + e.target.value);
        }}
      />
    </div>
  );
};

export default Search;
```

### Why Cancelling In-Flight Requests is Important

Cancelling in-flight requests is important here because it prevents a bug where multiple requests are made for the same query, leading to duplicate data being fetched. This can happen when the user rapidly types a query, causing multiple in-flight requests to be triggered before the previous request has a chance to complete.

By cancelling the in-flight request when a new query is started, we ensure that only one request is active at a time, preventing duplicate data from being fetched. This improves the performance and accuracy of the search feature.

*Response time: 9.4s*

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
I'd be happy to help you with each of these questions.

1. To fetch the 10 most recent published posts with the required information, you can use the following Prisma query:

```prisma
const recentPosts = await prisma.post.findMany({
  take: 10,
  where: {
    published: true,
  },
  include: {
    author: true,
    tags: true,
    comments: false,
  },
  select: {
    id: true,
    title: true,
    content: true,
    author: {
      select: {
        name: true,
      },
    },
    tags: {
      select: {
        name: true,
      },
    },
  },
})
```

This query fetches the 10 most recent published posts, including the author's name and tag names, without fetching the comments.

2. To add a slug field to the Post model safely without downtime, you can create a migration like this:

```javascript
module.exports = {
  up: async (queryInterface, Sequelize) => {
    await queryInterface.addColumn('Post', 'slug', {
      type: Sequelize.STRING,
      allowNull: false,
      unique: true,
    });
  },
  down: async (queryInterface, Sequelize) => {
    await queryInterface.removeColumn('Post', 'slug');
  },
}
```

This migration adds a new column `slug` to the `Post` table, making it unique and non-nullable.

3. To diagnose and fix the slow query, let's walk through the steps:

a. The Prisma query for finding posts filtered by tag name is:

```prisma
const filteredPosts = await prisma.post.findMany({
  include: {
    tags: true,
  },
  where: {
    tags: {
      some: {
        name: 'exampleTag',
      },
    },
  },
})
```

b. When you run this query, Prisma generates the following raw SQL:

```sql
SELECT "post".* FROM "post" JOIN "tag" ON "post".id = "tag".postId WHERE "tag".name = $1;
```

c. The slow query is caused by the lack of an index on the `tags` table. To fix this, you can add a unique index on the `tags` table:

```sql
CREATE INDEX idx_tags_name ON tags (name);
```

This index will speed up the query by allowing PostgreSQL to quickly find the matching tag.

4. You should drop down to raw SQL when the query is complex and doesn't fit into the Prisma query language, such as when using advanced PostgreSQL features like window functions or Common Table Expressions (CTEs).

For example, let's say you want to find the top 10 authors with the most published posts:

```prisma
const topAuthors = await prisma.$queryRaw`
  SELECT author.name, COUNT(*) as postCount
  FROM post
  JOIN author ON post.authorId = author.id
  GROUP BY author.name
  ORDER BY postCount DESC
  LIMIT 10;
`
```

In this case, you wouldn't be able to use Prisma's query language to achieve the same result, so you'd have to drop down to raw SQL.

*Response time: 8.2s*

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
**1. docker-compose.yml for local development**

```yml
version: '3'

services:
  frontend:
    build: .
    command: npm run start
    environment:
      - VITE_ENV=development
      - VITE_PORT=3000
    ports:
      - "3000:3000"
    volumes:
      - .:/app
    restart: always

  backend:
    build: .
    command: npm run start
    environment:
      - VITE_ENV=development
      - VITE_PORT=3000
    ports:
      - "3000:3000"
    depends_on:
      - postgresql
    healthcheck:
      test: ["curl -s -f http://localhost:3000/health

*Response time: 2.4s*

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
# Collaborative Document Editor Server Implementation

## Connection Handling

To associate a WebSocket connection with a user and document, we'll use a combination of session management and a data structure to store all connected users and their corresponding documents.

```javascript
const express = require('express');
const app = express();
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

const connectionMap = new Map();
const documentMap = new Map();

app.use(express.static('public'));

wss.on('connection', (ws) => {
  console.log('Client connected');

  ws.on('message', (message) => {
    const { type, data } = JSON.parse(message);

    switch (type) {
      case 'join_document':
        joinDocument(ws, data.documentId);
        break;
      case 'text_change':
        textChange(ws, data.documentId, data.position, data.text);
        break;
      case 'cursor_move':
        cursorMove(ws, data.documentId, data.position);
        break;
      case 'user_left':
        userLeft(ws, data.userId);
        break;
      default:
        console.log('Unknown message type');
    }
  });

  ws.on('close', () => {
    console.log('Client disconnected');

    // Remove client from connection map
    const userId = ws.userId;
    connectionMap.delete(userId);

    // Remove document from document map if no other users are connected
    if (!documentMap.has(data.documentId)) {
      documentMap.delete(data.documentId);
    }

    // Update connection map and document map
    const connectedUsers = Array.from(connectionMap.values());
    const documents = Array.from(documentMap.keys());

    for (const document of documents) {
      if (connectedUsers.includes(ws.userId)) {
        documentMap.set(document, connectedUsers.filter((id) => id !== ws.userId));
      }
    }
  });

  ws.on('reconnection', () => {
    console.log('Client reconnected');
  });

  ws.userId = data.userId;
});
```

## Message Protocol

The message protocol consists of three main message types:

### 1. `join_document`

*   `type`: `join_document`
*   `documentId`: `string` - ID of the document to join
*   `userId`: `string` - ID of the user making the request

Example:
```json
{
  "type": "join_document",
  "documentId": "doc-123",
  "userId": "user-1"
}
```

### 2. `text_change`

*   `type`: `text_change`
*   `documentId`: `string` - ID of the document being modified
*   `position`: `number` - position in the document where the text change occurs
*   `text`: `string` - text to be inserted or replaced

Example:
```json
{
  "type": "text_change",
  "documentId": "doc-123",
  "position": 10,
  "text": "Hello, world!"
}
```

### 3. `cursor_move`

*   `type`: `cursor_move`
*   `documentId`: `string` - ID of the document being modified
*   `position`: `number` - position in the document where the cursor moves

Example:
```json
{
  "type": "cursor_move",
  "documentId": "doc-123",
  "position": 20
}
```

### 4. `user_left`

*   `type`: `user_left`
*   `userId`: `string` - ID of the user disconnecting

Example:
```json
{
  "type": "user_left",
  "userId": "user-2"
}
```

## Broadcasting

When a user makes a change, the server broadcasts the message to all other users in the same document, excluding the user who made the change.

```javascript
const broadcast = (message, userId) => {
  if (documentMap.has(message.documentId)) {
    const connectedUsers = documentMap.get(message.documentId);
    if (!connectedUsers.includes(userId)) {
      connectedUsers.forEach((id) => {
        wss.clients.find((client) => client.userId === id).send(JSON.stringify(message));
      });
    }
  }
};
```

## Reconnection

To handle a user rejoining after disconnect, the server updates the connection map and document map.

```javascript
const joinDocument = (ws, documentId) => {
  ws.on('message', (message) => {
    const { type, data } = JSON.parse(message);

    switch (type) {
      case 'join_document':
        // Update connection map
        connectionMap.set(data.userId, ws);
        // Update document map
        if (!documentMap.has(data.documentId)) {
          documentMap.set(data.documentId, []);
        }
        documentMap.get(data.documentId).push(data.userId);

        // Broadcast initial message
        broadcast({
          type: 'text_change',
          documentId,
          position: 0,
          text: '',
        }, data.userId);

        break;
      default:
        console.log('Unknown message type');
    }
  });

  ws.on('message', (message) => {
    const { type, data } = JSON.parse(message);

    switch (type) {
      case 'text_change':
        broadcast(data, data.userId);
        break;
      case 'cursor_move':
        broadcast(data, data.userId);
        break;
      case 'user_left':
        // Remove user from document map
        const userId = data.userId;
        documentMap.get(data.documentId).splice(documentMap.get(data.documentId).indexOf(userId), 1);
        // Update connection map
        connectionMap.delete(userId);
        break;
      default:
        console.log('Unknown message type');
    }
  });
};
```

## Handling Concurrent Edits

When two users edit the exact same position simultaneously, the server should implement some mechanism to handle the conflict.

There are two approaches to handle concurrent edits:

### 1. **Last Writer Wins (LWW)**

In this approach, the server keeps track of the last user to make a change at a given position. If two users try to make a change at the same position, the server updates the position with the text from the last user to make a change.

### 2. **Merge Changes**

In this approach, the server merges the changes made by both users. It keeps a history of changes and merges the changes from both users, creating a new change that combines the changes from both users.

Both approaches have their own advantages and disadvantages. The LWW approach is simpler to implement but may lead to data loss if multiple users try to make changes at the same position. The merge changes approach can lead to more accurate results but is more complex to implement.

It's worth noting that implementing a fully functional collaborative editing system with concurrent edits can be complex and may require additional features such as undo/redo, versioning, and conflict resolution.

*Response time: 16.9s*

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
**Complete GraphQL Schema (SDL) for the Recipe Domain**

```graphql
type Recipe {
  id: ID!
  title: String!
  ingredients: [Ingredient!]!
  steps: [Step!]!
  author: Author!
  tags: [Tag!]!
  ratings: [Rating!]!
  averageRating: Float!
}

type Author {
  id: ID!
  name: String!
}

type Ingredient {
  id: ID!
  name: String!
  amount: Float!
  unit: String!
}

type Step {
  id: ID!
  description: String!
}

type Tag {
  id: ID!
  name: String!
}

type Rating {
  id: ID!
  score: Float!
  comment: String!
}

type Query {
  recipes(filter: RecipeFilter, pagination: Pagination): [Recipe!]!
  recipe(id: ID!): Recipe!
}

type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String!): Boolean!
}

type RecipeFilter {
  tag: String
  minRating: Float
}

type Pagination {
  page: Int
  limit: Int
}

type Subscription {
  recipeUpdated(id: ID!): Boolean!
}
```

**Resolvers for the Queries and Mutations**

```javascript
const resolvers = {
  Query: {
    recipes: async (parent, { filter, pagination }, context, info) => {
      const { skip, limit } = pagination;
      const recipes = await Recipe.findAndCountAll({
        where: {
          tags: {
            $in: filter.tag,
          },
          ratings: {
            avg: {
              $gt: filter.minRating,
            },
          },
        },
        offset: skip,
        limit,
      });

      return recipes;
    },
    recipe: async (parent, { id }, context, info) => {
      return Recipe.findById(id);
    },
  },
  Mutation: {
    addRating: async (parent, { recipeId, score, comment }, context, info) => {
      const recipe = await Recipe.findById(recipeId);
      if (!recipe) {
        throw new Error("Recipe not found");
      }

      const rating = new Rating({ recipe, score, comment });
      await rating.save();

      return true;
    },
  },
  Recipe: {
    averageRating: ({ ratings }) => {
      return ratings.reduce((acc, rating) => acc + rating.score, 0) / ratings.length;
    },
  },
};
```

**Fixing the N+1 Problem using DataLoader**

The N+1 problem occurs when the `recipes` query fetches multiple recipes and then fetches the author of each recipe individually. This can result in a large number of database queries.

To fix this problem, we can use DataLoader to preload the authors for all recipes. Here's an updated version of the `recipes` resolver:

```javascript
const DataLoader = require('dataloader');

const recipeLoader = new DataLoader(async (recipeIds) => {
  const recipes = await Recipe.findAndCountAll({
    where: {
      id: {
        $in: recipeIds,
      },
    },
  });

  const authors = await Promise.all(recipes.map((recipe) => Author.findById(recipe.authorId)));

  return recipes.map((recipe, index) => ({ ...recipe, author: authors[index] }));
}, {
  cache: true,
  capacity: 100,
});

const resolvers = {
  Query: {
    recipes: async (parent, { filter, pagination }, context, info) => {
      const { skip, limit } = pagination;
      const recipeIds = await recipeLoader.loadMany(filter.tag, filter.minRating);
      const recipes = await recipeLoader.loadMany(recipeIds, skip, limit);

      return recipes;
    },
    // ...
  },
};
```

In this updated resolver, we create a DataLoader instance that loads the recipes and their corresponding authors in a single query. We then use the `loadMany` method to load the recipes with their authors.

**GraphQL Query for fetching recipe title + author name + first 3 ingredients**

```graphql
query {
  recipe(id: "some-recipe-id") {
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

**When to choose GraphQL over REST**

Choose GraphQL over REST when:

* You have a complex, nested data structure that requires multiple, interconnected queries.
* You need to provide real-time updates and event-driven interactions.
* You want to optimize for performance and reduce the number of HTTP requests.
* You need to support large amounts of data and efficient querying.

**When not to choose GraphQL over REST**

Choose REST over GraphQL when:

* You have a simple, flat data structure that can be easily queried with standard HTTP methods.
* You need to support a large number of users and high traffic volumes.
* You prefer a more traditional, RESTful API architecture.
* You need to support caching and optimistic updates.

Note that GraphQL is not a replacement for REST; it's a complementary technology that can be used in conjunction with REST to provide a more efficient and scalable API.

*Response time: 12.6s*

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
Below is the complete HTML + CSS to implement the required UI layout:

HTML:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="header">
        <h1>HEADER</h1>
    </div>
    <div class="container">
        <div class="sidebar">
            <div class="sidebar-content">
                <h2>SIDEBAR</h2>
                <p>This is the sidebar content.</p>
            </div>
        </div>
        <div class="main-content">
            <div class="main-content-content">
                <h2>MAIN CONTENT</h2>
                <div class="cards">
                    <div class="card">
                        <img src="image1.jpg" alt="Image 1">
                        <h3>Title 1</h3>
                        <p>Description 1</p>
                        <footer>
                            <button>Button 1</button>
                            <button>Button 2</button>
                        </footer>
                    </div>
                    <div class="card">
                        <img src="image2.jpg" alt="Image 2">
                        <h3>Title 2</h3>
                        <p>Description 2</p>
                        <footer>
                            <button>Button 3</button>
                            <button>Button 4</button>
                        </footer>
                    </div>
                    <div class="card">
                        <img src="image3.jpg" alt="Image 3">
                        <h3>Title 3</h3>
                        <p>Description 3</p>
                        <footer>
                            <button>Button 5</button>
                            <button>Button 6</button>
                        </footer>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
```

CSS:
```css
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: Arial, sans-serif;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
}

.header {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 60px;
    background-color: #333;
    color: #fff;
    padding: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.container {
    padding-top: 60px;
    display: flex;
    flex-direction: row;
    height: calc(100vh - 60px);
}

.sidebar {
    width: 240px;
    height: 100%;
    overflow-y: auto;
    background-color: #f0f0f0;
    padding: 20px;
}

.sidebar-content {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.main-content {
    width: calc(100% - 240px);
    height: 100%;
    overflow-y: auto;
    background-color: #f0f0f0;
    padding: 20px;
}

.main-content-content {
    display: flex;
    flex-direction: column;
}

.cards {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-gap

*Response time: 9.2s*

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
**Designing the Notification System**

### 1. Transport Mechanism

For real-time notifications, we'll use **WebSockets** as the transport mechanism. Here's why:

* **Bi-directional communication**: WebSockets enable bidirectional communication between the client and server, allowing for real-time updates.
* **Low latency**: WebSockets provide low latency, ensuring that notifications are delivered quickly.
* **Scalability**: WebSockets can handle a large number of concurrent connections, making them suitable for a large user base.
* **Efficient**: WebSockets use a single connection to establish communication, reducing overhead compared to polling or push notifications.

### 2. Storing Notifications

We'll use a **NoSQL database**, specifically **MongoDB**, to store notifications. The database schema will be as follows:

```json
// notifications collection
{
  "_id": ObjectId,
  "userId": String,
  "taskId": String,
  "type": String (e.g., "taskAssigned", "commentAdded", "deadlineApproaching"),
  "data": Object (e.g., task details, comment text),
  "createdAt": Date,
  "updatedAt": Date
}
```

This schema allows for efficient storage and retrieval of notifications based on user IDs, task IDs, and notification types.

### 3. Handling Offline Users

To handle offline users, we'll use a combination of **WebSockets** and **message queueing**. When a user goes offline, their WebSocket connection is closed, and a message is added to a queue (e.g., RabbitMQ). When the user comes back online, the WebSocket connection is reopened, and the message is processed.

Here's a simplified example of how this works:

```javascript
// When a user goes offline
userDisconnected();

// When the user comes back online
userConnected();

// Process the message from the queue
processNotificationMessage(message);
```

This approach ensures that offline users don't miss notifications when they come back online.

### 4. Implementing Deadline Check

To implement the deadline check, we'll use an **event-driven approach** with a **cron job**. We'll create a separate service responsible for checking deadlines every hour and pushing notifications to users who need them.

Here's an example implementation:

```bash
# cron job
0 * * * * node /path/to/deadlineChecker.js
```

```javascript
// deadlineChecker.js
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

setInterval(checkDeadlines, 3600000); // Check deadlines every 1 hour

function checkDeadlines() {
  // Check deadlines for all tasks
  const tasks = getTasks();
  tasks.forEach((task) => {
    const deadline = task.deadline;
    if (deadline < new Date()) {
      // Send notifications to users who need them
      sendNotifications(task, deadline);
    }
  });
}

function sendNotifications(task, deadline) {
  const users = getUsersForTask(task);
  users.forEach((user) => {
    // Send notification to user
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify({ type: 'deadlineApproaching', data: { task, deadline } }));
      }
    });
  });
}
```

This implementation checks deadlines every hour and pushes notifications to users who need them, ensuring that users receive timely notifications.

### 5. Scaling the System

To scale the system for 100,000 concurrent users, we'll use a combination of **horizontal partitioning**, **load balancing**, and **content delivery networks (CDNs)**.

Here's a high-level overview of the scaling approach:

1. **Horizontal partitioning**: Shard the database across multiple instances, each handling a portion of the user base. This ensures that the system can handle a large number of concurrent users.
2. **Load balancing**: Use a load balancer to distribute incoming traffic across the shards, ensuring that each shard handles a manageable load.
3. **CDNs**: Use a CDN to cache static resources, reducing the load on the system and improving overall performance.
4. **Caching**: Implement caching mechanisms (e.g., Redis) to store frequently accessed data, reducing the load on the database.
5. **Auto-scaling**: Implement auto-scaling mechanisms to dynamically add or remove instances based on system load, ensuring that the system can handle changes in user traffic.

By using this scaling approach, the system can handle a large number of concurrent users while maintaining performance and reliability.

*Response time: 11.1s*

---
