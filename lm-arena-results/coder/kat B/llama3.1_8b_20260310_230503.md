# Model: llama3.1:8b
**Test Date:** 2026-03-10 23:29:21
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
**API Endpoints**

### Workspace

* `POST /workspaces` - Create a new workspace
* `GET /workspaces/{workspaceId}` - Retrieve a workspace by ID
* `GET /workspaces/{workspaceId}/projects` - Retrieve projects for a workspace
* `GET /workspaces/{workspaceId}/users` - Retrieve users for a workspace

### Project

* `POST /workspaces/{workspaceId}/projects` - Create a new project in a workspace
* `GET /workspaces/{workspaceId}/projects/{projectId}` - Retrieve a project by ID
* `GET /workspaces/{workspaceId}/projects/{projectId}/tasks` - Retrieve tasks for a project
* `PUT /workspaces/{workspaceId}/projects/{projectId}` - Update a project

### Task

* `POST /workspaces/{workspaceId}/projects/{projectId}/tasks` - Create a new task in a project
* `GET /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}` - Retrieve a task by ID
* `PUT /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/status` - Update task status
* `PUT /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/assignee` - Update task assignee
* `PUT /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/due-date` - Update task due date
* `GET /workspaces/{workspaceId}/projects/{projectId}/tasks` - Retrieve tasks for a project with filters (assignee, status, due date)
* `GET /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments` - Retrieve comments for a task

### User

* `POST /workspaces/{workspaceId}/users` - Create a new user in a workspace
* `GET /workspaces/{workspaceId}/users/{userId}` - Retrieve a user by ID

### Comment

* `POST /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments` - Create a new comment for a task
* `GET /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments/{commentId}` - Retrieve a comment by ID

**Request/Response JSON Shapes**

### Create Task

Request:
```json
{
  "title": "New Task",
  "description": "Task description",
  "project_id": 1,
  "assignee_id": 1,
  "due_date": "2023-03-15"
}
```
Response:
```json
{
  "id": 1,
  "title": "New Task",
  "description": "Task description",
  "project_id": 1,
  "assignee_id": 1,
  "due_date": "2023-03-15",
  "status": "pending"
}
```

### Update Task Status

Request:
```json
{
  "status": "in_progress"
}
```
Response:
```json


*Response time: 14.4s*

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
Here is the implementation of the endpoint in Node.js + Express + TypeScript:

**validation.ts**
```typescript
import { z } from 'zod';

const workspaceIdSchema = z.number().positive();
const taskIdSchema = z.number().positive();

const taskUpdateSchema = z.object({
  title: z.string().min(1, { message: 'Title is required' }).max(200, { message: 'Title must not exceed 200 characters' }),
  status: z.enum(['todo', 'in_progress', 'done', 'cancelled']).optional(),
  assignee_id: z.number().optional().nullable(),
  due_date: z.string().optional().nullable(),
});

export { workspaceIdSchema, taskIdSchema, taskUpdateSchema };
```

**task.controller.ts**
```typescript
import { Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import { workspaceIdSchema, taskIdSchema, taskUpdateSchema } from './validation';
import { Task, Workspace, User } from '../models';

const updateTask = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const workspaceId = parseInt(req.params.workspaceId, 10);
    const taskId = parseInt(req.params.taskId, 10);

    await workspaceIdSchema.parse(workspaceId);
    await taskIdSchema.parse(taskId);

    const task = await Task.findOne({
      where: { id: taskId, workspace_id: workspaceId },
      include: [{ model: User, as: 'assignee' }],
    });

    if (!task) {
      return res.status(404).json({ message: 'Task not found' });
    }

    const { assignee_id, due_date } = req.body;

    if (assignee_id) {
      const user = await User.findOne({ where: { id: assignee_id } });
      if (!user || !await user.isMemberOfWorkspace(workspaceId)) {
        return res.status(400).json({ message: 'Assignee must be a member of the workspace' });
      }
    }

    const updatedTask = await task.update({
      title: req.body.title,
      status: req.body.status,
      assignee_id,
      due_date,
    });

    if (req.body.status === 'cancelled' && updatedTask.subtasks.some((subtask) => subtask.status !== 'done')) {
      return res.status(409).json({ message: 'Cannot set status to cancelled with open subtasks' });
    }

    return res.json(updatedTask);
  } catch (error) {
    next(error);
  }
};

export { updateTask };
```

**task.middleware.ts**
```typescript
import { NextFunction, Request, Response } from 'express';
import { ErrorRequestHandler } from 'express-async-errors';
import { Task, Workspace } from '../models';

const errorMiddleware = async (err: Error, req: Request, res: Response, next: NextFunction) => {
  if (err instanceof ErrorRequestHandler) {
    if (err.status === 404) {
      return res.status(404).json({ message: 'Not found' });
    }

    const validationErrors = err.validationErrors;
    if (validationErrors) {
      const errors = validationErrors.map((error) => ({ [error.path]: error.message }));

      return res.status(400).json({ errors });
    }
  }

  next(err);
};

export { errorMiddleware };
```

**task.controller.unit.test.ts**
```typescript
import { updateTask } from './task.controller';
import { Task, Workspace, User } from '../models';
import { Request, Response } from 'express';
import { errorMiddleware } from './task.middleware';
import { workspaceIdSchema, taskIdSchema, taskUpdateSchema } from './validation';

describe('updateTask', () => {
  it('success', async () => {
    const workspace = await Workspace.create({ name: 'Test Workspace' });
    const task = await Task.create({ title: 'Test Task', workspace_id: workspace.id, status: 'todo' });
    const user = await User.create({ email: 'test@example.com', password: 'password' });
    await user.addMemberToWorkspace(workspace);

    const req: Request = { params: { workspaceId: workspace.id.toString(), taskId: task.id.toString() }, body: { title: 'Updated Title' } };
    const res: Response = { json: jest.fn() };

    await updateTask(req, res);
    expect(res.json).toHaveBeenCalledTimes(1);
    expect(res.json).toHaveBeenCalledWith(task);
  });

  it('validation error', async () => {
    const workspace = await Workspace.create({ name: 'Test Workspace' });
    const task = await Task.create({ title: 'Test Task', workspace_id: workspace.id, status: 'todo' });

    const req: Request = { params: { workspaceId: workspace.id.toString(), taskId: task.id.toString() }, body: { title: 'Updated Title' } };
    const res: Response = { json: jest.fn() };

    await updateTask(req, res);
    expect(res.json).toHaveBeenCalledTimes(1);
    expect(res.json).toHaveBeenCalledWith({ errors: [{ title: 'Title is required' }] });
  });

  it('404', async () => {
    const workspace = await Workspace.create({ name: 'Test Workspace' });

    const req: Request = { params: { workspaceId: workspace.id.toString(), taskId: 'non-existent-task-id' }, body: { title: 'Updated Title' } };
    const res: Response = { json: jest.fn() };

    await updateTask(req, res);
    expect(res.json).toHaveBeenCalledTimes(1);
    expect(res.json).toHaveBeenCalledWith({ message: 'Not found' });
  });

  it('409', async () => {
    const workspace = await Workspace.create({ name: 'Test Workspace' });
    const task = await Task.create({ title: 'Test Task', workspace_id: workspace.id, status: 'todo' });
    const subtask = await Task.create({ title: 'Test Subtask', workspace_id: workspace.id, status: 'in_progress', task_id: task.id });

    const req: Request = { params: { workspaceId: workspace.id.toString(), taskId: task.id.toString() }, body: { status: 'cancelled' } };
    const res: Response = { json: jest.fn() };

    await updateTask(req, res);
    expect(res.json).toHaveBeenCalledTimes(1);
    expect(res.json).toHaveBeenCalledWith({ message: 'Cannot set status to cancelled with open subtasks' });
  });
});
```

Note that this is a basic implementation and you may need to adapt it to your specific use case and database schema. Additionally, this implementation assumes that you are using Sequelize as your ORM, if you are using a different ORM, you may need to adjust the code accordingly.

*Response time: 32.2s*

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
Here is an example implementation of the authentication system using Node.js, Express, and TypeScript:

**dependencies**

* `express`: `^4.17.1`
* `bcrypt`: `^5.0.1`
* `jsonwebtoken`: `^8.5.1`
* `typescript`: `^4.1.3`
* `ts-node`: `^10.2.1`

**auth.controller.ts**
```typescript
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { Request, Response } from 'express';

interface User {
  id: string;
  email: string;
  role: string;
}

class AuthController {
  async register(req: Request, res: Response) {
    const { email, password } = req.body;
    const hashedPassword = await bcrypt.hash(password, 12);
    const user: User = { id: '1234567890', email, role: 'user' };
    res.json(user);
  }

  async login(req: Request, res: Response) {
    const { email, password } = req.body;
    const user: User = { id: '1234567890', email, role: 'user' };
    const payload = {
      userId: user.id,
      email: user.email,
      role: user.role,
      iat: Math.floor

*Response time: 6.8s*

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
Based on your previous auth system, I'll provide the implementation details for the additional requirements.

**1. POST /auth/refresh**

To implement the refresh token rotation, we'll use a Redis-based token store. We'll store the refresh token in Redis with a unique identifier, along with the user's ID and a timestamp.

**Redis Data Structure:**

```markdown
+----------------+------------+------------+
| Token ID      | User ID    | Timestamp  |
+----------------+------------+------------+
| refresh_token_1| user_123  | 1643723400 |
| refresh_token_2| user_123  | 1643723400 |
+----------------+------------+------------+
```

**TTL Strategy:**

We'll set a TTL (time-to-live) of 30 days for each refresh token. This means that if a refresh token is not used within 30 days, it will be automatically expired and removed from the Redis store.

**Implementation:**

```python
import redis
from datetime import datetime, timedelta

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Function to rotate refresh token
def rotate_refresh_token(user_id, old_refresh_token):
    # Get the current timestamp
    now = int(datetime.now().timestamp())

    # Generate a new refresh token
    new_refresh_token = generate_refresh_token()

    # Store the new refresh token in Redis
    redis_client.hset('refresh_tokens', new_refresh_token, user_id, now)

    # Invalidate the old refresh token
    redis_client.expire(old_refresh_token, 30 * 24 * 60 * 60)  # 30 days

    # Return the new refresh token
    return new_refresh_token

# Function to issue a new access token using the refresh token
def issue_access_token(refresh_token):
    # Get the user ID associated with the refresh token
    user_id = redis_client.hget('refresh_tokens', refresh_token)

    # If the refresh token is invalid or expired, return an error
    if not user_id:
        return {'error': 'Invalid refresh token'}

    # Issue a new access token
    access_token = generate_access_token(user_id)

    # Return the access token
    return {'access_token': access_token}

# POST /auth/refresh endpoint
@app.route('/auth/refresh', methods=['POST'])
def refresh_token():
    # Get the refresh token from the request
    refresh_token = request.cookies.get('refresh_token')

    # If the refresh token is not provided, return an error
    if not refresh_token:
        return {'error': 'Refresh token not provided'}

    # Rotate the refresh token and issue a new access token
    new_refresh_token = rotate_refresh_token(user_id, refresh_token)
    access_token = issue_access_token(new_refresh_token)

    # Return the access token
    return access_token
```

**2. POST /auth/logout**

To implement the logout functionality, we'll simply invalidate the refresh token and clear the cookie.

```python
# POST /auth/logout endpoint
@app.route('/auth/logout', methods=['POST'])
def logout():
    # Get the refresh token from the request
    refresh_token = request.cookies.get('refresh_token')

    # If the refresh token is not provided, return an error
    if not refresh_token:
        return {'error': 'Refresh token not provided'}

    # Invalidate the refresh token
    redis_client.expire(refresh_token, 0)  # Immediately expire the refresh token

    # Clear the cookie
    response = make_response('Logged out successfully')
    response.set_cookie('refresh_token', '', expires=0)

    # Return a success message
    return response
```

**3. Refresh Token Rotation with Redis**

We've already implemented the refresh token rotation using Redis in the previous section.

**4. Token Reuse Detection**

To detect token reuse, we'll store the last used timestamp for each refresh token in Redis. If the refresh token is used again within a certain time window (e.g., 5 minutes), we'll consider it a reuse attempt.

```python
# Redis data structure for last used timestamps
+----------------+------------+
| Token ID      | Last Used  |
+----------------+------------+
| refresh_token_1| 1643723400 |
| refresh_token_2| 1643723400 |
+----------------+------------+

# Function to update the last used timestamp for a refresh token
def update_last_used_timestamp(refresh_token):
    # Get the current timestamp
    now = int(datetime.now().timestamp())

    # Update the last used timestamp in Redis
    redis_client.hset('last_used_timestamps', refresh_token, now)

# Function to check for token reuse
def check_token_reuse(refresh_token):
    # Get the last used timestamp for the refresh token
    last_used_timestamp = redis_client.hget('last_used_timestamps', refresh_token)

    # If the refresh token is not used within the last 5 minutes, return True
    if not last_used_timestamp or (int(datetime.now().timestamp()) - int(last_used_timestamp) > 5 * 60):
        return True

    # If the refresh token is reused within the last 5 minutes, return False
    return False
```

**5. Invalidating Existing Sessions**

To invalidate all existing sessions for a user, we'll simply expire all refresh tokens associated with the user's ID in Redis.

```python
# Function to invalidate all existing sessions for a user
def invalidate_sessions(user_id):
    # Get all refresh tokens associated with the user's ID
    refresh_tokens = redis_client.hkeys('refresh_tokens')

    # Expire all refresh tokens
    for token in refresh_tokens:
        redis_client.expire(token, 0)  # Immediately expire the refresh token
```

**6. Token Blacklisting vs. Token Rotation**

**Token Blacklisting:**

Token blacklisting involves storing a list of invalid tokens in a database or cache. When a token is blacklisted, it is marked as invalid and cannot be used to authenticate. Token blacklisting is typically used for short-term security measures, such as after a user has been compromised or a token has been leaked.

**Token Rotation:**

Token rotation involves regularly rotating tokens (e.g., access tokens or refresh tokens) to prevent token reuse and reduce the impact of a token being compromised. Token rotation is typically used for long-term security measures, such as to ensure that tokens are periodically updated and refreshed.

In summary, token blacklisting is used for short-term security measures, while token rotation is used for long-term security measures. Both techniques can be used together to provide an additional layer of security.

*Response time: 31.7s*

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
Here's the implementation of the DataTable component in React + TypeScript:

**DataTableProps interface**
```typescript
interface DataTableProps<T> {
  columns: DataTableColumn[];
  data: T[];
  selectedRows: T[];
  onSelectRow: (row: T) => void;
  onSortColumn: (column: DataTableColumn, ascending: boolean) => void;
  onPageSizeChange: (pageSize: number) => void;
  pageSizes: number[];
  pagination: boolean;
  currentPage: number;
  renderFooter?: () => React.ReactNode;
}
```
**DataTableColumn interface**
```typescript
interface DataTableColumn {
  key: string;
  header: string;
  width: number;
  sortable: boolean;
  renderCell?: (row: any) => React.ReactNode;
}
```
**DataTable component implementation**
```typescript
import React, { useState, memo } from 'react';

interface DataTableState {
  selectedRows: any[];
  sortColumn: DataTableColumn | null;
  ascending: boolean;
}

const DataTable = <T,>({
  columns,
  data,
  selectedRows,
  onSelectRow,
  onSortColumn,
  onPageSizeChange,
  pageSizes,
  pagination,
  currentPage,
  renderFooter,
}: DataTableProps<T>) => {
  const [state, setState] = useState<DataTableState>({
    selectedRows: selectedRows || [],
    sortColumn: null,
    ascending: false,
  });

  const handleRowSelect = (row: T) => {
    setState((prev) => ({ ...prev, selectedRows: [...prev.selectedRows, row] }));
    onSelectRow(row);
  };

  const handleSortColumn = (column: DataTableColumn, ascending: boolean) => {
    setState((prev) => ({ ...prev, sortColumn: column, ascending }));
    onSortColumn(column, ascending);
  };

  const handlePageSizeChange = (pageSize: number) => {
    onPageSizeChange(pageSize);
  };

  const handleSelectAll = () => {
    setState((prev) => ({ ...prev, selectedRows: data }));
    onSelectRow(...data);
  };

  const handleDeselectAll = () => {
    setState((prev) => ({ ...prev, selectedRows: [] }));
    onSelectRow(null);
  };

  const renderHeader = () => {
    return (
      <thead>
        <tr>
          {columns.map((column) => (
            <th key={column.key}>
              {column.header}
              {column.sortable && (
                <span className="sort-icon">
                  {state.sortColumn === column ? (
                    state.ascending ? (
                      <i className="fas fa-sort-up" />
                    ) : (
                      <i className="fas fa-sort-down" />
                    )
                  ) : (
                    <i className="fas fa-sort" />
                  )}
                </span>
              )}
            </th>
          ))}
        </tr>
      </thead>
    );
  };

  const renderBody = () => {
    const sortedData = data.sort((a, b) => {
      if (state.sortColumn && state.sortColumn.key) {
        const aValue = a[state.sortColumn.key];
        const bValue = b[state.sortColumn.key];
        return aValue < bValue ? -1 : 1;
      }
      return 0;
    });

    const rows = sortedData.map((row, index) => (
      <tr key={index}>
        {columns.map((column) => (
          <td key={column.key}>
            {column.renderCell ? (
              column.renderCell(row)
            ) : (
              row[column.key]
            )}
          </td>
        ))}
        <td>
          <input
            type="checkbox"
            checked={state.selectedRows.includes(row)}
            onChange={() => handleRowSelect(row)}
          />
        </td>
      </tr>
    ));

    return (
      <tbody>
        {rows}
      </tbody>
    );
  };

  const renderFooter = () => {
    if (renderFooter) {
      return renderFooter();
    }
    return (
      <tfoot>
        <tr>
          <td colSpan={columns.length + 1}>
            {pagination && (
              <div>
                <button onClick={() => handlePageSizeChange(10)}>10 rows/page</button>
                <button onClick={() => handlePageSizeChange(25)}>25 rows/page</button>
                <button onClick={() => handlePageSizeChange(50)}>50 rows/page</button>
              </div>
            )}
            <button onClick={handleSelectAll}>Select All</button>
            <button onClick={handleDeselectAll}>Deselect All</button>
          </td>
        </tr>
      </tfoot>
    );
  };

  return (
    <table>
      {renderHeader()}
      {renderBody()}
      {renderFooter()}
    </table>
  );
};

export default memo(DataTable);
```
**Usage example**
```typescript
import React from 'react';
import DataTable from './DataTable';

const columns = [
  { key: 'id', header: 'ID', width: 100, sortable: true },
  { key: 'name', header: 'Name', width: 200, sortable: true },
  { key: 'action', header: 'Action', width: 100, sortable: false, renderCell: (row) => <button>View</button> },
];

const data = [
  { id: 1, name: 'John Doe', action: 'View' },
  { id: 2, name: 'Jane Doe', action: 'View' },
  { id: 3, name: 'Bob Smith', action: 'View' },
];

const App = () => {
  const [selectedRows, setSelectedRows] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);

  const handleSortColumn = (column, ascending) => {
    // ...
  };

  const handlePageSizeChange = (pageSize) => {
    // ...
  };

  const handleSelectRow = (row) => {
    // ...
  };

  return (
    <DataTable
      columns={columns}
      data={data}
      selectedRows={selectedRows}
      onSelectRow={handleSelectRow}
      onSortColumn={handleSortColumn}
      onPageSizeChange={handlePageSizeChange}
      pageSizes={[10, 25, 50]}
      pagination={true}
      currentPage={currentPage}
      renderFooter={() => (
        <tfoot>
          <tr>
            <td colSpan={columns.length + 1}>
              <button onClick={() => setCurrentPage(2)}>Next Page</button>
            </td>
          </tr>
        </tfoot>
      )}
    />
  );
};
```
**Memoization**

To memoize the `DataTable` component correctly, we can use the `memo` function from React to cache the component's props and return the cached component instance if the props are the same. We can also use the `useCallback` hook to memoize the `handleSortColumn`, `handlePageSizeChange`, and `handleSelectRow` functions.

Here's the updated code:
```typescript
import { memo, useCallback } from 'react';

const DataTable = memo((props: DataTableProps<T>) => {
  // ...
});

const handleSortColumn = useCallback((column, ascending) => {
  // ...
}, []);

const handlePageSizeChange = useCallback((pageSize) => {
  // ...
}, []);

const handleSelectRow = useCallback((row) => {
  // ...
}, []);

// ...
```
By memoizing the `DataTable` component and its functions, we can avoid unnecessary re-renders and improve the component's performance.

*Response time: 36.3s*

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
Here is the implementation in React using hooks only:

**useSearch hook**
```js
import { useState, useEffect, useCallback } from 'react';
import { fetch } from 'node-fetch';

const useSearch = (query) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cache, setCache] = useState({});

  const debouncedQuery = useCallback(
    (query) => {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve(query);
        }, 300);
      });
    },
    []
  );

  useEffect(() => {
    const cachedResult = cache[query];
    if (cachedResult) {
      setResults(cachedResult);
    } else {
      setLoading(true);
      const cancelSource = fetch(
        `/api/search?q=${encodeURIComponent(query)}`
      )
        .then((response) => response.json())
        .then((data) => {
          setResults(data);
          setCache((prevCache) => ({ ...prevCache, [query]: data }));
        })
        .catch((error) => {
          setError(error);
        })
        .finally(() => {
          setLoading(false);
        });
      return () => {
        cancelSource.cancel();
      };
    }
  }, [query, cache]);

  return { results, loading, error };
};
```
**SearchPage component**
```js
import React from 'react';
import { useSearch } from './useSearch';
import './SearchPage.css';

const SearchPage = () => {
  const [searchQuery, setSearchQuery] = React.useState('');
  const { results, loading, error } = useSearch(searchQuery);

  const handleSearch = (e) => {
    e.preventDefault();
    setSearchQuery(e.target.searchQuery.value);
  };

  return (
    <div>
      <form onSubmit={handleSearch}>
        <input type="search" name="searchQuery" />
        <button type="submit">Search</button>
      </form>
      {loading ? (
        <div>Loading...</div>
      ) : error ? (
        <div>
          <p>Error: {error.message}</p>
          <button onClick={() => setSearchQuery('')}>
            Retry
          </button>
        </div>
      ) : (
        <ul>
          {results.map((result) => (
            <li key={result.id}>{result.name}</li>
          ))}
        </ul>
      )}
    </div>
  );
};
```
**URL sync implementation**
```js
import { useHistory, useLocation } from 'react-router-dom';

const useSearchQuery = () => {
  const history = useHistory();
  const location = useLocation();

  const query = location.search.slice(1);

  const handleSearch = (newQuery) => {
    history.replace(`?q=${encodeURIComponent(newQuery)}`);
  };

  return [query, handleSearch];
};
```
And use it in the `SearchPage` component:
```js
import React from 'react';
import { useSearchQuery } from './useSearchQuery';
import SearchPage from './SearchPage';

const SearchPageWrapper = () => {
  const [query, setQuery] = useSearchQuery();

  return (
    <SearchPage
      searchQuery={query}
      onChange={(newQuery) => setQuery(newQuery)}
    />
  );
};
```
**Why is cancelling in-flight requests important?**

When the user starts a new search, we want to cancel any in-flight requests for the previous search. If we don't cancel these requests, we'll end up with multiple requests to the API, which can lead to duplicate results, or worse, a server error.

For example, suppose the user types "search term" and then immediately types "new search term". If we don't cancel the in-flight request for "search term", we'll end up with two requests to the API: one for "search term" and one for "new search term". This can lead to duplicate results or server errors.

By cancelling in-flight requests, we ensure that only one request is made to the API for each search query, which prevents duplicate results and server errors.

**Bug prevented by cancelling in-flight requests**

One possible bug that can be prevented by cancelling in-flight requests is the following:

* Suppose the user types a search query, but the API takes a long time to respond. Meanwhile, the user types a new search query and submits it. If we don't cancel the in-flight request for the first search query, we'll end up with two requests to the API: one for the first search query and one for the second search query. When the first request finally responds, it will return outdated results, which can lead to confusion for the user.

By cancelling in-flight requests, we ensure that only one request is made to the API for each search query, which prevents outdated results and confusion for the user.

*Response time: 23.5s*

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

To fetch the 10 most recent published posts with author name, tag names, and comment count without triggering N+1 queries, we'll use a single query that fetches the data in one operation. Prisma's built-in support for relations and eager loading helps us achieve this.

```prisma
query {
  posts(
    where: { published: true },
    take: 10,
    orderBy: { createdAt: desc }
  ) {
    id
    title
    content
    author {
      id
      name
    }
    tags {
      name
    }
    comments {
      count
    }
  }
}
```

Prisma's generated SQL will use a single query to fetch all the required data, preventing N+1 issues.

### 2. Adding a Slug Field to Post with Minimal Downtime

To add a slug field to the Post model without downtime, we can use a two-step migration process:

1. **Create a new column with a default value**: First, we add a new column with a default value. This way, when we insert new data, the slug will be generated on the fly.

   ```prisma
   model Post {
     // ...
     slug String @default(cuid());
   }
   ```

   We then update our application to use this new column.

2. **Fill in existing data**: Once the new field is in place, we can create a migration to populate the slug field for existing records. Prisma provides the `db` command to execute database operations, including migrations.

   ```prisma
   npx prisma migrate dev --name "add-slug-field"
   ```

   Then, we write a Prisma query to update the `slug` field:

   ```prisma
   model Post {
     // ...
     slug String @unique @db.VarChar(255)
   }

   prisma db seed
   prisma db update post set slug = cuid() where id in (select id from post)
   ```

   This will update the slug field for all existing posts.

### 3. Optimizing Slow Query: Filtering by Tag Name

Let's say we have the following Prisma query:

```prisma
query {
  posts(where: { tags: { some: { name: "example-tag" } } }) {
    id
    title
    content
  }
}
```

Prisma might generate a SQL query like this:

```sql
SELECT "id", "title", "content"
FROM "public"."post"
WHERE "public"."post"."id" = ANY (
  SELECT "id"
  FROM "public"."tag"
  WHERE "name" = $1
);
```

This query would scan the `tag` table for every row in the `post` table, leading to performance issues. To optimize this, we need to add an index on the `name` column of the `tag` table.

```prisma
model Tag {
  // ...
  name String @unique @index(createdAt)
}
```

Prisma uses `@index(createdAt)` to create an index on the `name` column. This will speed up the query significantly because the database can now directly access the `tag` records matching the filter criteria.

### 4. When to Drop Down to Raw SQL

While Prisma is a powerful ORM, there are scenarios where direct SQL queries are necessary. Here's a real example:

Suppose we need to perform a bulk update on the `Post` table, changing the `published` status of all posts with a certain tag. Prisma's ORM does not support bulk updates in this scenario efficiently. We would need to drop down to raw SQL to achieve this:

```sql
UPDATE post SET published = true
FROM post
JOIN tag ON post.id = tag.post_id
WHERE tag.name = 'example-tag';
```

This direct SQL query is more efficient and straightforward for this specific use case. Prisma provides a `db` command to execute raw SQL queries. 

```prisma
prisma db raw `UPDATE post SET published = true FROM post JOIN tag ON post.id = tag.post_id WHERE tag.name = 'example-tag';`
```

*Response time: 20.2s*

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
**1. Docker-compose.yml for local development**

```yml
version: '3'

services:
  frontend:
    build: ./frontend
    volumes:
      - ./frontend:/app
      - ./node_modules:/app/node_modules
    environment:
      - VITE_API_URL=http://localhost:3001
    ports:
      - "3000:3000"
    depends_on:
      - backend

  backend:
    build: ./backend
    volumes:
      - ./backend:/app
      - ./node_modules:/app/node_modules
      - ./backend/.env:/app/.env
    environment:
      - DB_HOST=postgres
      - DB_USER=postgres
      - DB_PASSWORD=postgres
    ports:
      - "3001:3001"
    healthcheck:
      test: ["CMD", "pg-isready", "-U", "postgres"]
      interval: 10s
      timeout: 5s
      retries: 3
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - pg-data:/var/lib/postgresql/data

  redis:
    image: redis

volumes:
  pg-data:
```

This configuration sets up the frontend and backend services with hot reload, using the `vite` and `nodemon` scripts. PostgreSQL and Redis are also set up as separate services, with PostgreSQL having a named volume for persistence. Environment variables are read from a `.env` file in the backend directory.

**2. Production Dockerfile for the backend**

```Dockerfile
# builder stage
FROM node:14 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# production stage
FROM node:14 AS runtime
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/.env ./
RUN npm run build
RUN npm run production

# final image
FROM node:14 AS final
WORKDIR /app
COPY --from=runtime /app/dist ./dist
USER node
EXPOSE 3001
CMD ["npm", "start"]
```

This Dockerfile sets up a multi-stage build, with the builder stage installing dependencies and the production stage building the application. The final image runs as the `node` user and only includes the production dependencies.

**3. Diagnosis of exit code 137**

Exit code 137 usually indicates that the process has been killed by the kernel due to a segmentation fault or a lack of memory. In the case of a Node.js application, this can be caused by a number of issues, including:

* Running out of memory
* Reaching the maximum number of open file descriptors
* Reaching the maximum number of concurrent connections

To diagnose the issue, you can try:

* Checking the application logs for any error messages
* Monitoring the system resources (e.g. memory usage, CPU usage) to see if the application is consuming excessive resources
* Checking the Node.js process for any signs of memory leaks or other issues

**4. Deployment sequence with zero downtime**

To deploy a new version of the application with zero downtime, you can follow these steps:

1. **Database schema changes**: Make any necessary database schema changes in a separate database, using a tool like `pg_dump` and `pg_restore`.
2. **Build new image**: Build a new Docker image with the updated application code.
3. **Deploy new image**: Deploy the new image to a new set of containers, using a load balancer to route traffic to both the old and new containers.
4. **Switch to new image**: Once the new containers are up and running, switch the load balancer to route all traffic to the new containers.
5. **Remove old containers**: Once the new containers are fully serving traffic, remove the old containers and any remaining resources.
6. **Verify database schema**: Verify that the database schema has been updated correctly in the new containers.
7. **Test application**: Test the application thoroughly to ensure that it is functioning correctly with the updated database schema.

Note: This is a simplified sequence and may require additional steps depending on your specific deployment setup and requirements.

*Response time: 20.8s*

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
Here's a simplified implementation of the server-side functionality using Node.js and the ws library.

### Connection Handling

We'll use a `Map` to store connections, where each connection is associated with a `UserDocument` object.
```javascript
const WebSocket = require('ws');
const connections = new Map();

class UserDocument {
  constructor(userId, documentId) {
    this.userId = userId;
    this.documentId = documentId;
    this.cursors = {}; // Map of cursor IDs to positions
    this.text = '';
  }
}
```

### Message Protocol

We define the message types as JSON objects:
```javascript
const messageTypes = {
  JOIN_DOCUMENT: 'joinDocument',
  TEXT_CHANGE: 'textChange',
  CURSOR_MOVE: 'cursorMove',
  USER_LEFT: 'userLeft',
};
```

### Broadcasting

We'll use a `Map` to store the users connected to each document.
```javascript
const documentUsers = new Map();

// When a user joins a document, add them to the document's users list
function joinDocument(userId, documentId) {
  const userDocument = new UserDocument(userId, documentId);
  connections.set(userId, userDocument);
  if (!documentUsers.has(documentId)) {
    documentUsers.set(documentId, new Set());
  }
  documentUsers.get(documentId).add(userId);
}

// When a user makes a change, broadcast it to all other users in the same document
function broadcastChange(documentId, message) {
  const users = documentUsers.get(documentId);
  if (users) {
    users.forEach((userId) => {
      if (userId !== message.userId) {
        const userDocument = connections.get(userId);
        userDocument.text = message.text;
        userDocument.cursors[message.cursorId] = message.position;
      }
    });
    broadcastToUsers(documentId, message);
  }
}

function broadcastToUsers(documentId, message) {
  const users = documentUsers.get(documentId);
  if (users) {
    users.forEach((userId) => {
      const userDocument = connections.get(userId);
      userDocument.text = message.text;
      userDocument.cursors[message.cursorId] = message.position;
      // Send the message to the user's client
      userDocument.ws.send(JSON.stringify(message));
    });
  }
}
```

### Reconnection

When a user reconnects, we update their `UserDocument` object to reflect the latest document state.
```javascript
function reconnect(userId, documentId) {
  const userDocument = connections.get(userId);
  if (userDocument) {
    const documentUsers = documentUsers.get(documentId);
    if (documentUsers) {
      documentUsers.forEach((otherUserId) => {
        const otherUserDocument = connections.get(otherUserId);
        otherUserDocument.text = userDocument.text;
        otherUserDocument.cursors = userDocument.cursors;
      });
    }
  }
}
```

### Core Server Implementation

```javascript
const WebSocketServer = require('ws').Server;

const wss = new WebSocketServer({ port: 8080 });

wss.on('connection', (ws) => {
  let userId;
  ws.on('message', (message) => {
    const { type, documentId } = JSON.parse(message);
    switch (type) {
      case messageTypes.JOIN_DOCUMENT:
        userId = message.userId;
        joinDocument(userId, documentId);
        break;
      case messageTypes.TEXT_CHANGE:
        const textChangeMessage = {
          type: messageTypes.TEXT_CHANGE,
          text: message.text,
          cursorId: message.cursorId,
          position: message.position,
          userId,
        };
        broadcastChange(documentId, textChangeMessage);
        break;
      case messageTypes.CURSOR_MOVE:
        const cursorMoveMessage = {
          type: messageTypes.CURSOR_MOVE,
          cursorId: message.cursorId,
          position: message.position,
          userId,
        };
        broadcastChange(documentId, cursorMoveMessage);
        break;
      case messageTypes.USER_LEFT:
        // Remove the user from the document's users list
        documentUsers.get(documentId).delete(userId);
        break;
    }
  });

  ws.on('close', () => {
    // Remove the user from the connections map
    connections.delete(userId);
    // Remove the user from the document's users list
    documentUsers.get(documentId).delete(userId);
  });

  ws.on('reconnect', () => {
    reconnect(userId, documentId);
  });

  // Send the initial document state to the user's client
  const userDocument = connections.get(userId);
  if (userDocument) {
    const documentStateMessage = {
      type: messageTypes.JOIN_DOCUMENT,
      text: userDocument.text,
      cursors: userDocument.cursors,
    };
    ws.send(JSON.stringify(documentStateMessage));
  }
});
```

### Simultaneous Edits

When two users edit the same position simultaneously, there are a few possible solutions:

1. **Last Writer Wins (LWW)**: The last edit is the one that is applied. This approach is simple to implement but can lead to lost updates.
2. **Vector Clocks**: Assign a vector clock to each document, which keeps track of the edit history. When two users edit the same position, the vector clock is used to determine which edit is applied.
3. **Operational Transformation (OT)**: Each user's edits are represented as a sequence of operations (e.g., insert, delete, replace). When two users edit the same position, their operations are transformed to produce a consistent edit history.
4. **Conflict-Free Replicated Data Types (CRDTs)**: A CRDT is a data structure that can be updated concurrently by multiple users without conflicts.

For a simple implementation, we can use LWW. However, for a more robust solution, we would recommend using vector clocks or OT.

*Response time: 27.8s*

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
Here are the answers to your questions:

**1. Complete GraphQL Schema (SDL)**

```graphql
type Author {
  id: ID!
  name: String!
}

type Ingredient {
  name: String!
  amount: Float!
  unit: String!
}

type Rating {
  score: Float!
  comment: String
}

type Tag {
  id: ID!
  name: String!
}

type Recipe {
  id: ID!
  title: String!
  ingredients: [Ingredient!]!
  steps: [String!]!
  author: Author!
  tags: [Tag!]!
  ratings: [Rating!]!
  averageRating: Float @formula(avgRating: [Rating])
}

union QueryResult = Recipe

type Query {
  recipes(filter: RecipeFilter, pagination: PaginationInput): [Recipe!]!
}

input RecipeFilter {
  tag: String
  minRating: Float
}

input PaginationInput {
  page: Int
  limit: Int
}

type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String!): Rating!
}
```

**2. Resolvers for Query.recipes**

```javascript
const resolvers = {
  Query: {
    recipes: async (parent, { filter, pagination }, { db }) => {
      const { page, limit } = pagination;
      const { tag, minRating } = filter;

      const recipes = await db.recipes.findMany({
        where: {
          ...(tag && { tags: { some: { name: tag } } }),
          ...(minRating && { averageRating: { gt: minRating } }),
        },
        skip: (page - 1) * limit,
        take: limit,
      });

      return recipes;
    },
  },
  Mutation: {
    addRating: async (parent, { recipeId, score, comment }, { db }) => {
      const rating = await db.ratings.create({
        data: { recipe: { connect: { id: recipeId } }, score, comment },
      });

      return rating;
    },
  },
};
```

Note: `db.recipes` and `db.ratings` are assumed to be database models for the recipe and rating tables.

**3. Resolver for Recipe.averageRating**

```javascript
const resolvers = {
  Recipe: {
    averageRating: async (recipe, _, { db }) => {
      const ratings = await db.ratings.findMany({
        where: { recipe: { id: recipe.id } },
      });

      if (!ratings.length) return 0;

      const scores = ratings.map((rating) => rating.score);
      const sum = scores.reduce((acc, curr) => acc + curr, 0);
      return sum / scores.length;
    },
  },
};
```

**4. N+1 problem with Query.recipes and DataLoader**

Let's say we have a recipe with 10 ratings, and each rating has an author. If we fetch the recipe's ratings using `db.ratings.findMany`, we'll end up making 11 database queries:

1. `db.recipes.findMany` (1 query)
2. `db.ratings.findMany` (1 query)
3. `db.authors.findMany` (1 query) for each rating (10 queries)

To fix this, we can use a DataLoader, which caches and batches database queries. Here's an example using `apollo-dataloader`:

```javascript
const { DataLoader } = require('apollo-dataloader');

const authorLoader = new DataLoader((authorIds) => {
  return db.authors.findMany({
    where: { id: { in: authorIds } },
  });
});

const resolvers = {
  Recipe: {
    ratings: async (recipe) => {
      const ratingIds = recipe.ratings.map((rating) => rating.id);
      const ratings = await db.ratings.findMany({
        where: { id: { in: ratingIds } },
      });

      const authors = await authorLoader.loadMany(ratingIds.map((id) => id));

      return ratings.map((rating) => ({
        ...rating,
        author: authors.find((author) => author.id === rating.author.id),
      }));
    },
  },
};
```

**5. Client query to fetch recipe title, author name, and first 3 ingredients**

```graphql
query {
  recipe(id: "recipe-123") {
    title
    author {
      name
    }
    ingredients(limit: 3) {
      name
      amount
      unit
    }
  }
}
```

**6. When to choose GraphQL over REST**

Choose GraphQL over REST when:

* You need to fetch multiple related resources in a single request (e.g., fetching a user's posts and comments).
* You have a high number of fields or queries, and want to reduce the number of requests.
* You want to enable client-side caching and reduce the number of requests.
* You want to provide a flexible and evolving API that can adapt to changing client needs.

**When to NOT choose GraphQL**

Choose REST over GraphQL when:

* You have a simple API with a small number of resources and fields.
* You prioritize simplicity and ease of implementation over flexibility and scalability.
* You have a strict requirement for strict schema enforcement and validation.
* You're working with a legacy system or technology stack that doesn't support GraphQL.

*Response time: 25.3s*

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
**HTML:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Responsive UI Layout</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="header">
        <h1>Header</h1>
    </header>
    <div class="container">
        <aside class="sidebar">
            <h2>Sidebar</h2>
            <ul>
                <li><a href="#">Link 1</a></li>
                <li><a href="#">Link 2</a></li>
                <!-- ... -->
            </ul>
        </aside>
        <main class="main-content">
            <div class="cards">
                <div class="card">
                    <img src="image1.jpg" alt="Card 1">
                    <h3>Card 1 Title</h3>
                    <p>Description of Card 1</p>
                    <footer>
                        <button class="left-button">Left Button</button>
                        <button class="right-button">Right Button</button>
                    </footer>
                </div>
                <div class="card">
                    <img src="image2.jpg" alt="Card 2">
                    <h3>Card 2 Title</h3>
                    <p>Description of Card 2</p>
                    <footer>
                        <button class="left-button">Left Button</button>
                        <button class="right-button">Right Button</button>
                    </footer>
                </div>
                <!-- ... -->
            </div>
        </main>
    </div>
</body>
</html>
```
**CSS (in style.css file):**
```css
body, html {
    height: 100%;
    margin: 0;
    padding: 0;
}

.header {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 60px;
    background-color: #333;
    color: #fff;
    padding: 1em;
    box-sizing: border-box;
}

.container {
    display: flex;
    flex-direction: column;
    height: calc(100% - 60px);
}

.sidebar {
    position: relative;
    flex-grow: 0;
    flex-shrink: 0;
    width: 240px;
    padding: 1em;
    background-color: #f7f7f7;
    overflow-y: auto;
}

.main-content {
    flex-grow: 1;
    flex-shrink: 1;
    padding: 1em;
    overflow-y: auto;
}

.cards {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1em;
    margin: -1em;
    padding: 1em;
}

.card {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background-color: #fff;
    padding: 1em;
    border: 1px solid #ddd;
    border-radius: 0.25em;
}

.card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    aspect-ratio: 16/9;
}

footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5em;
}

.left-button {
    margin-right: 0.5em;
}

.right-button {
    margin-left: 0.5em;
}

/* Media query for mobile layout */
@media (max-width: 768px) {
    .cards {
        grid-template-columns: 1fr;
    }
}
```
**Layout Approach:**

We use a combination of Flexbox and CSS Grid to achieve the desired layout.

1. The outermost container (`<div class="container">`) uses Flexbox to arrange its children in a column direction. This allows the sidebar and main content to fill the remaining space below the header.
2. The sidebar (`<aside class="sidebar">`) has a fixed width of 240px and uses Flexbox to arrange its content vertically. We use `flex-grow` and `flex-shrink` to ensure the sidebar maintains its size while the main content scrolls independently.
3. The main content (`<main class="main-content">`) uses Flexbox to fill the remaining space and scroll independently.
4. The cards (`<div class="cards">`) use CSS Grid to arrange their content in a responsive grid layout. We use `grid-template-columns` to define two columns for desktop layouts and one column for mobile layouts.
5. Each card (`<div class="card">`) uses Flexbox to arrange its content in a column direction, with the image taking up the full height and width. We use `object-fit` and `aspect-ratio` to maintain the image's 16:9 ratio.

Note that we use media queries to adjust the grid layout for mobile devices. In this example, we define two columns for desktop layouts and one column for mobile layouts. You can adjust the media query breakpoints and grid layout as needed to accommodate different screen sizes and device types.

*Response time: 25.5s*

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
I'll outline the design for the notification system based on your requirements.

**1. Transport Mechanism**

After considering various transport mechanisms, I recommend using WebSockets for real-time notifications. Here's why:

*   **Real-time updates**: WebSockets enable bi-directional communication between the client and server, allowing for real-time updates and immediate notification delivery.
*   **Efficient use of resources**: WebSockets maintain a persistent connection, reducing the overhead of establishing a new connection for each notification.
*   **Scalability**: WebSockets can handle a large number of concurrent connections, making them suitable for a project management tool with 100,000 concurrent users.

Other options, such as polling or push notifications, may not provide the same level of real-time updates and efficiency.

**2. Database Schema**

To store notifications, I suggest the following database schema:

```sql
CREATE TABLE notifications (
    id INT PRIMARY KEY,
    user_id INT,  // foreign key referencing the users table
    task_id INT,  // foreign key referencing the tasks table
    type VARCHAR(255),  // e.g., 'assignment', 'comment', 'deadline'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP NULL
);

CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(255) UNIQUE
);

CREATE TABLE tasks (
    id INT PRIMARY KEY,
    title VARCHAR(255),
    deadline DATE
);
```

This schema stores notifications in a separate table, with foreign keys referencing the users and tasks tables. The `type` column indicates the type of notification (assignment, comment, or deadline). The `created_at` column records the time the notification was created, and the `read_at` column indicates when the user read the notification (if applicable).

**3. Handling Offline Users**

To handle users who are offline, we can use the following approach:

*   When a user is online, they establish a WebSocket connection with the server.
*   When a new notification is generated, the server sends a notification to the user's WebSocket connection.
*   If the user is offline, the notification is stored in the database and sent to the user when they come back online.

To ensure that offline users receive missed notifications, we can implement a mechanism to check for unread notifications when the user logs in or comes back online. This can be done by:

*   Retrieving the user's unread notifications from the database.
*   Sending the notifications to the user's WebSocket connection.

**4. Implementing Deadline Check**

To implement the deadline check, I recommend using an event-driven approach:

*   Create a separate process or service responsible for checking deadlines every hour.
*   Use a scheduling library (e.g., cron job) or a message queue (e.g., RabbitMQ, Apache Kafka) to trigger the deadline check process at regular intervals (e.g., every hour).
*   When a deadline is approaching (within 24 hours), generate a notification and send it to the relevant user's WebSocket connection.

Here's an example implementation using a cron job and a scheduling library:

```bash
# crontab configuration
0 * * * * /path/to/deadline-check.sh
```

```bash
#!/bin/bash

# Load environment variables
. /path/to/env.sh

# Run deadline check
python /path/to/deadline-check.py
```

```python
import datetime
import json

# Define a function to check deadlines
def check_deadlines():
    # Retrieve tasks with approaching deadlines
    tasks = db.query(Task).filter(Task.deadline <= datetime.datetime.now() + datetime.timedelta(hours=24))

    # Generate notifications for each task
    for task in tasks:
        notification = {
            'type': 'deadline',
            'task_id': task.id
        }
        # Send notification to relevant user's WebSocket connection
        send_notification(notification)

# Run deadline check every hour
while True:
    check_deadlines()
    time.sleep(3600)
```

**5. Scaling for 100,000 Concurrent Users**

To scale the notification system for 100,000 concurrent users, consider the following strategies:

*   **Distributed architecture**: Deploy the notification system on a distributed architecture (e.g., microservices, containerization) to ensure that each component can handle a large number of connections.
*   **Load balancing**: Use load balancing techniques (e.g., round-robin, least connections) to distribute incoming connections across multiple instances of the notification system.
*   **Caching**: Implement caching mechanisms (e.g., Redis, Memcached) to reduce the load on the database and improve notification delivery performance.
*   **Queueing**: Use message queues (e.g., RabbitMQ, Apache Kafka) to handle a high volume of notifications and ensure that each user receives their notifications in a timely manner.

By implementing these strategies, you can ensure that the notification system can handle a large number of concurrent users and provide a seamless user experience.

*Response time: 23.2s*

---
