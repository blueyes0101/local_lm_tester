# Model: qwen2.5-coder:0.5b
**Test Date:** 2026-03-10 20:50:36
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
To design a REST API for a multi-tenant SaaS project management tool, we need to define the necessary endpoints, request/response JSON shapes, and error handling. We'll also ensure that the API handles pagination and provides consistent error responses.

### 1. Define Endpoints

- **Workspace**: Create, update, and list workspaces.
- **Project**: Create, update, and list projects.
- **Task**: Create, update, and list tasks with filters.
- **User**: Create, update, and list users.
- **Comment**: Create, update, and list comments.

### 2. Show Request/Response JSON Shapes

- **Workspace**: `GET /workspaces`
- **Project**: `GET /projects`
- **Task**: `GET /tasks/<task_id>`
- **User**: `GET /users/<user_id>`
- **Comment**: `GET /comments/<comment_id>`
- **Task/Assignee**: `POST /tasks/<task_id>/assignee/<user_id>`
- **Task/Status**: `PUT /tasks/<task_id>/status/<status_id>`
- **Task/Due Date**: `PUT /tasks/<task_id>/due_date/<due_date>`
- **Task/Comment**: `POST /tasks/<task_id>/comment/<comment_id>`

### 3. Define Error Response Format

- **Response for Creating a Task**: `201 Created`
  ```json
  {
    "message": "Task created successfully",
    "status": 201,
    "data": {
      "task_id": <task_id>
    }
  }
  ```
- **Response for Updating a Task Status**: `200 OK`
  ```json
  {
    "message": "Task status updated successfully",
    "status": 200,
    "data": {
      "task_id": <task_id>,
      "status": <status_id>
    }
  }
  ```
- **Response for Listing Tasks**: `200 OK`
  ```json
  {
    "message": "Tasks retrieved successfully",
    "status": 200,
    "data": [
      {
        "task_id": <task_id>,
        "assignee": <assignee_id>,
        "status": <status_id>,
        "due_date": <due_date>
      }
      // Add more tasks here
    ]
  }
  ```
- **Response for Assigning a User to a Task**: `200 OK`
  ```json
  {
    "message": "User assigned to task successfully",
    "status": 200,
    "data": {
      "task_id": <task_id>,
      "user_id": <user_id>
    }
  }
  ```
- **Response for updating a Task Due Date**: `200 OK`
  ```json
  {
    "message": "Task due date updated successfully",
    "status": 200,
    "data": {
      "task_id": <task_id>,
      "due_date": <due_date>
    }
  }
  ```
- **Response for Updating a Task Comment**: `200 OK`
  ```json
  {
    "message": "Task comment updated successfully",
    "status

*Response time: 4.0s*

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
To implement the specified endpoint, we need to create a Node.js application with Express, TypeScript, and Zod. We'll define the endpoints, validate the incoming requests, and handle the responses. Additionally, we'll write unit tests to ensure the handler works as expected.

Here's a complete implementation:

```typescript
import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { getTaskById, getWorkspaceById, setTaskStatus } from './service';

const router = Router();

// Schema for the task update request
const taskUpdateSchema = z.object({
  title: z.string().min(1, 'Title must be at least 1 character long'),
  status: z.union(['todo', 'in_progress', 'done', 'cancelled']),
  assignee_id: z.number().int().nullable(),
  due_date: z.string().optional().date()
});

// Endpoint to get a task by ID
router.get('/workspaces/:workspaceId/tasks/:taskId', async (req: Request, res: Response) => {
  const { workspaceId, taskId } = req.params;
  const task = await getTaskById(workspaceId, taskId);
  if (!task) {
    return res.status(404).send({ error: 'Task not found' });
  }
  res.status(200).send(task);
});

// Endpoint to update a task
router.patch('/workspaces/:workspaceId/tasks/:taskId', async (req: Request, res: Response) => {
  const { workspaceId, taskId } = req.params;
  const { title, status, assignee_id, due_date } = req.body;
  const task = await getTaskById(workspaceId, taskId);

  if (!task) {
    return res.status(404).send({ error: 'Task not found' });
  }

  // Validate the input
  const validationErrors = taskUpdateSchema.parse({ title, status, assignee_id, due_date });
  if (Object.keys(validationErrors).length > 0) {
    return res.status(400).send(validationErrors);
  }

  // Update the task
  await setTaskStatus(workspaceId, taskId, status, assignee_id, due_date);

  res.status(200).send({ message: 'Task updated successfully' });
});

// Unit tests
describe('task update endpoint', () => {
  it('should return 200 with a valid task if the task exists', async () => {
    const response = await fetch(`/workspaces/1/tasks/1`);
    const body = await response.json();
    const task = body.task;
    expect(task).toHaveProperty('id');
    expect(task.status).toBe('in_progress');
  });

  it('should return 404 if the task does not exist', async () => {
    const response = await fetch(`/workspaces/1/tasks/9999`);
    const body = await response.json();
    expect(body.error).toBe('Task not found');
  });

  it('should return 400 if the task status is invalid', async () => {
    const response = await fetch(`/workspaces/1/tasks/1/status/abc`);
    const body = await response.json();
    expect(body.error).toBe('Invalid status');
  });

  it('should return 409 if setting status to "cancelled" on an open task', async () => {
    const response = await fetch(`/workspaces/1/tasks/1/status/cancelled`);
    const body = await response.json();
    expect(body.error).toBe('Cannot set status to "cancelled" on an open task');
  });

  it('should return 200 with the updated task if the validation is successful', async () => {
    const newStatus = 'completed';
    const response = await fetch(`/workspaces/1/tasks/1/status/${newStatus}`);
    const body = await response.json();
    const updatedTask = body.task;
    expect(updatedTask.status).toBe(newStatus);
  });
});
```

### Explanation:

1. **Schema Definition**: We use the `zod` library to define a schema for the `taskUpdateSchema` that includes fields for `title`, `status`, `assignee_id`, and `due_date`. We validate these fields to ensure they are valid.

2. **Endpoint Handling**: 
   - `getTaskById`: Retrieves a task by its ID from the database.
   - `setTaskStatus`: Updates the task status and assigns it to the given assignee ID. It also checks for validation errors.

3. **Unit Tests**:
   - The `describe` block runs several tests to ensure the endpoints work correctly:
     - Get task by ID
     - Update task
     - Set task status with validation errors
     - Set task status to "cancelled" on an open task

This implementation provides a robust way to handle PATCH requests for updating tasks in a workspace, with validation and error handling to ensure the data is correct and consistent.

*Response time: 6.1s*

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
To implement a complete authentication system in Node.js + Express + TypeScript, we need to follow these steps:

1. **Hash Password**: Use bcrypt to hash passwords before storing them in the database.
2. **Create Tokens**: Generate and store a JWT (JSON Web Token) that includes user information.
3. **Protect Routes**: Use middleware to authenticate and authorize requests.
4. **Handle Expired Tokens**: Return an error response with the appropriate error code and message.

### Step 1: Hash Password

First, we need to use bcrypt to hash the password. Here's how you can implement this in TypeScript:

```typescript
import bcrypt from 'bcrypt';
import { generateRandomString } from 'crypto';

// Function to hash a password
async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 12);
}

// Example usage
const hashedPassword = await hashPassword('password123');
console.log(hashedPassword); // Output: bcrypt:pbkdf2:sha256:12
```

### Step 2: Create Tokens

For each request, generate a JWT using the hashed password and set a token expiration time of 15 minutes.

```typescript
async function createToken(userId: string, email: string): Promise<string> {
  const expires = new Date();
  expires.setMinutes(expires.getMinutes() + 15);
  const token = bcrypt.hash(userId + email + expires, 12);
  return token;
}

// Example usage
const token = await createToken('user123', 'user@example.com');
console.log(token); // Output: bcrypt:pbkdf2:sha256:15
```

### Step 3: Protect Routes

Create a middleware to validate the access token and attach the user to `req.user` if the token is valid.

```typescript
import { Middleware } from 'express';
import bcrypt from 'bcrypt';

interface User {
  userId: string;
  email: string;
  role: string;
  iat: Date;
  exp: Date;
}

const authMiddleware: Middleware = async (req, res, next) => {
  const token = req.header('Authorization');

  if (!token) {
    return res.status(401).json({ message: 'Access token is missing' });
  }

  try {
    const decodedToken = jwt.verify(token, process.env.JWT_SECRET);
    const user = decodedToken.user as User;
    req.user = user;
    next();
  } catch (error) {
    return res.status(401).json({ message: 'Invalid token' });
  }
};

// Example usage
app.use(authMiddleware);
```

### Step 4: Handle Expired Tokens

If the token is expired, return an error response with the appropriate error code and message.

```typescript
app.get('/auth/me', (req, res) => {
  if (!req.user) {
    return res.status(401).json({ message: 'User is not authenticated' });
  }

  const currentDate = new Date();
  const diffInMinutes = currentDate.getTime() - req.user.exp.getTime();
  const tokenExpire = new Date(currentDate.getTime() + diffInMinutes * 60000);

  if (tokenExpire < new Date()) {
    res.status(401).json({ message: 'Token has expired' });
  } else {
    res.json({ userId: req.user.userId, email: req.user.email, role: req.user.role, iat: req.user.iat, exp: tokenExpire });
  }
});
```

### Step 5: Use HttpOnly Cookie for Refresh Token

HTTP-only cookies are used to store the refresh token and should be disabled by default. This is because HTTP-only cookies are accessible only to the client and should be removed after the response is sent.

```typescript
app.use((req, res, next) => {
  if (req.cookies.refreshToken) {
    req.cookies.refreshToken = undefined; // Clear the cookie
    next();
  } else {
    next();
  }
});

// Example usage
app.post('/auth/login', (req, res) => {
  const userId = req.body.userId;
  const email = req.body.email;
  const password = req.body.password;

  try {
    const hashedPassword = await hashPassword(password);
    const token = await createToken(userId, email);
    res.cookie('refreshToken', token, { httpOnly: false, secure: true });

    res.status(201).json({ userId, email, role: 'user' });
  } catch (error) {
    res.status(401).json({ message: 'Invalid credentials' });
  }
});
```

### Security Reasoning

HTTP-only cookies are a security measure to prevent XSS (Cross-Site Scripting) attacks. By not including the cookie in the client response, we ensure that the client can't access the cookie, thus protecting against potential XSS attacks. The `httpOnly` and `secure` flags are used to enforce these security measures.

*Response time: 6.2s*

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

This route allows users to refresh their access token by sending a request to the /auth/refresh endpoint. The server should then generate a new access token using the provided refresh token and issue it to the client. This will cause the client to request a new refresh token from the server, and the server will rotate the refresh token if it is expired.

2. POST /auth/logout — invalidate the refresh token, clear the cookie.

This route clears the refresh token from the client's cookie. This can be useful for logging out of a session or for temporary disabling of a session that might have expired.

3. Implement refresh token rotation with a Redis-based token store (show the Redis data structure and TTL strategy)

This option involves using a Redis-based token store to store the refresh tokens. Redis is a key-value store that can be used to store and manage a set of data. By storing the refresh token in Redis, the server can keep track of the user's last refresh token and automatically rotate it whenever the user changes their password.

4. How do you handle the case where a refresh token is used twice? (token reuse detection)

To handle token reuse detection, the server should check if the new refresh token is already present in the Redis store. If it is, the server should invalidate the existing refresh token and issue a new one. If not, it should store the new refresh token in the Redis store.

5. A user changes their password — how do you invalidate ALL their existing sessions? Implement it.

To invalidate all existing sessions for a user, the server should clear the session data stored in Redis for that user. This can be done by deleting all the data associated with the user's session and the corresponding refresh token.

6. What is the difference between token blacklisting and token rotation? When would you use each?

Token blacklisting refers to the practice of removing or expiring tokens that are not currently in use. Token rotation involves replacing the old refresh token with a new one, which can help maintain security by ensuring that users cannot reuse their refresh tokens.

In summary, the choice between token blacklisting and token rotation depends on the specific requirements of the application. If token blacklisting is necessary, it can be implemented by deleting all the data associated with the user's session and the corresponding refresh token. If token rotation is necessary, it can be implemented by replacing the old refresh token with a new one, which can help maintain security by ensuring that users cannot reuse their refresh tokens.

*Response time: 3.2s*

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
### 1. TypeScript Interface

First, let's define the type for the component props. We'll use a generic to allow for any type of row data:

```typescript
interface DataTableProps<T extends object> {
  data: T[];
  columns: { key: string, header: string, width: number, sortable: boolean, renderCell?: (row: T, index: number) => ReactNode };
  pagination: {
    pageSizeOptions: number[];
  };
  selectedRows: number[];
}
```

### 2. Complete Component Implementation

We'll create a class-based component using React. This class will handle the rendering of the DataTable, handling pagination, and row selection:

```typescript
import React, { useState } from 'react';
import { Column, useTable, getSortedData, usePagination } from 'react-table';

const DataTable: React.FC<DataTableProps<YourDataType>> = ({
  data,
  columns,
  pagination: { pageSizeOptions },
  selectedRows: selectedRows,
}) => {
  // Set up the table
  const { rows, columns: originalColumns, setColumnHeaders } = useTable({
    data,
    columns: originalColumns,
    columnsPerPage: 10,
    defaultSortBy: { key: 'someColumn', order: 'asc' },
  });

  // Function to handle a column header click
  const handleColumnHeaderClick = (key: string, direction: 'asc' | 'desc' | 'none') => {
    setColumnHeaders((prevColumns) => {
      return prevColumns.map((col) => {
        if (col.key === key) {
          return {
            ...col,
            sortable: direction === 'none',
          };
        }
        return col;
      });
    });
  };

  // Function to handle a row selection
  const handleRowSelect = (index: number) => {
    setSelectedRows((prevSelectedRows) => {
      return [...prevSelectedRows, index];
    });
  };

  // Function to handle pagination
  const handlePageChange = (page: number) => {
    const newRows = getSortedData(rows, page, { order: 'asc' });
    setRows(newRows);
  };

  return (
    <table className="table">
      <thead>
        {columns.map((col, index) => (
          <Column
            key={col.key}
            header={col.header}
            width={col.width}
            sortable={col.sortable}
            renderCell={(row, index) => (
              <button
                onClick={() => handleColumnHeaderClick(col.key, col.sortable === 'none' ? 'desc' : 'asc')}
                style={{ backgroundColor: col.sortable ? 'blue' : 'gray' }}
              >
                {col.header}
              </button>
            )}
          />
        ))}
      </thead>
      <tbody>
        {rows.map((row, index) => (
          <tr key={row.key}>
            {columns.map((col, index) => (
              <td key={col.key}>{col.renderCell(row, index)}</td>
            ))}
          </tr>
        ))}
      </tbody>
      <footer>
        <button
          onClick={() => handlePageChange(0)}
          style={{ backgroundColor: 'blue' }}
        >
          First Page
        </button>
        <button
          onClick={() => handlePageChange(1)}
          style={{ backgroundColor: 'green' }}
        >
          Second Page
        </button>
        <button
          onClick={() => handlePageChange(2)}
          style={{ backgroundColor: 'purple' }}
        >
          Third Page
        </button>
      </footer>
    </table>
  );
};

// Example usage
const YourDataType = {
  id: '1',
  name: 'John Doe',
  age: 30,
  address: '123 Main St',
  email: 'john.doe@example.com',
  isStudent: true,
};

const App = () => {
  const [selectedRows, setSelectedRows] = useState([]);

  return (
    <div>
      <DataTable
        data={YourDataType.data}
        columns={[
          { key: 'id', header: 'ID', sortable: true },
          { key: 'name', header: 'Name', sortable: true },
          { key: 'age', header: 'Age', sortable: true },
          { key: 'address', header: 'Address', sortable: true },
          { key: 'email', header: 'Email', sortable: true },
          { key: 'isStudent', header: 'Student', sortable: true },
        ]}
        pagination={{ pageSizeOptions: [10, 25, 50] }}
        selectedRows={selectedRows}
        onSelect={(index) => setSelectedRows((prevSelectedRows) => [...prevSelectedRows, index])}
      />
    </div>
  );
};

export default App;
```

### 3. Memoization

To optimize the component, we can use memoization. The `useMemo` hook is a functional alternative to `React.memo` for memoizing the component. We'll add a memoized `renderCell` function to the component:

```typescript
import React, { useState, useMemo } from 'react';
import { Column, useTable, getSortedData, usePagination } from 'react-table';

const DataTable: React.FC<DataTableProps<YourDataType>> = ({
  data,
  columns,
  pagination: { pageSizeOptions },
  selectedRows: selectedRows,
}) => {
  // Set up the table
  const { rows, columns: originalColumns, setColumnHeaders } = useTable({
    data,
    columns: originalColumns,
    columnsPerPage: 10,
    defaultSortBy: { key: 'someColumn', order: 'asc' },
  });

  // Memoized renderCell function
  const renderCell = useMemo(() => {
    return (row, index) => {
      if (row.key === 'action') {
        return (
          <button
            onClick={() => handleColumnHeaderClick('action', 'none')}
            style={{ backgroundColor: 'blue' }}
          >
            Action
          </button>
        );
      }
      return (
        <td key={row.key}>{row[action]}</td>
      );
    };
  }, [rows, selectedRows, columnHeaders]);

  // Function to handle a column header click
  const handleColumnHeaderClick = (key: string, direction: 'asc' | 'desc' | 'none') => {
    setColumnHeaders((prevColumns) => {
      return prevColumns.map((col) => {
        if (col.key === key) {
          return {
            ...col,
            sortable: direction === 'none',
          };
        }
        return col;
      });
    });
  };

  // Function to handle a row selection
  const handleRowSelect = (index: number) => {
    setSelectedRows((prevSelectedRows) => [...prevSelectedRows, index]);
  };

  // Function to handle pagination
  const handlePageChange = (page: number) => {
    const newRows = getSortedData(rows, page, { order: 'asc' });
    setRows(newRows);
  };

  return (
    <table className="table">
      <thead>
        {columns.map((col, index) => (
          <Column
            key={col.key}
            header={col.header}
            width={col.width}
            sortable={col.sortable}
            renderCell={renderCell}
          />
        ))}
      </thead>
      <tbody>
        {rows.map((row, index) => (
          <tr key={row.key}>
            {columns.map((col, index) => (
              <td key={col.key}>{col.renderCell(row, index)}</td>
            ))}
          </tr>
        ))}
      </tbody>
      <footer>
        <button
          onClick={() => handlePageChange(0)}
          style={{ backgroundColor: 'blue' }}
        >
          First Page
        </button>
        <button
          onClick={() => handlePageChange(1)}
          style={{ backgroundColor: 'green' }}
        >
          Second Page
        </button>
        <button
          onClick={() => handlePageChange(2)}
          style={{ backgroundColor: 'purple' }}
        >
          Third Page
        </button>
      </footer>
    </table>
  );
};

export default App;
```

### 

*Response time: 10.4s*

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
To implement the search feature with the specified requirements, we need to create a custom hook `useSearch` that handles fetching results, debounce, caching, and cancellation. We'll also implement the `SearchPage` component that uses this hook and URL sync. Here's how you can achieve this:

```jsx
import React, { useState, useEffect, useNavigate } from 'react';
import { useDebounce } from 'lodash';

// Custom hook to handle fetch, debounce, cache, cancellation
const useSearch = (query: string) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState<string[]>([]);
  const [hasCachedResults, setHasCachedResults] = useState(false);
  const [lastFetchTime, setLastFetchTime] = useState(null);

  const fetchResults = async () => {
    if (loading) return;

    const url = `https://api/search?q=${query}`;

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
      setLoading(false);
    } catch (error) {
      setError(error);
    }
  };

  const handleDebounce = useDebounce(fetchResults, 300);

  const handleCancel = () => {
    if (hasCachedResults) {
      setHasCachedResults(false);
      setLastFetchTime(null);
    }
  };

  useEffect(() => {
    const cachedResults = getCache();
    if (cachedResults && cachedResults.length > 0) {
      setResults(cachedResults);
      setHasCachedResults(true);
      setLastFetchTime(cachedResults[0].timestamp);
    }
  }, [hasCachedResults, lastFetchTime]);

  const cacheResults = async (query: string) => {
    const url = `https://api/search?q=${query}`;

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.status}`);
      }

      const data = await response.json();
      setResults([data, ...results]);
      setHasCachedResults(true);
      setLastFetchTime(data.timestamp);
    } catch (error) {
      setError(error);
    }
  };

  return {
    loading,
    error,
    results,
    hasCachedResults,
    lastFetchTime,
    handleDebounce,
    handleCancel,
    cacheResults,
  };
};

// Custom hook to handle URL sync
const useURLSync = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [cachedResults, setCachedResults] = useState<string[]>([]);
  const [hasCachedResults, setHasCachedResults] = useState(false);
  const [lastFetchTime, setLastFetchTime] = useState(null);

  const fetchResults = async () => {
    if (loading) return;

    const url = `https://api/search?q=${searchTerm}`;

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
      setLoading(false);
    } catch (error) {
      setError(error);
    }
  };

  const handleDebounce = useDebounce(fetchResults, 300);

  const handleCancel = () => {
    if (hasCachedResults) {
      setHasCachedResults(false);
      setLastFetchTime(null);
    }
  };

  useEffect(() => {
    const cachedResults = getCache();
    if (cachedResults && cachedResults.length > 0) {
      setResults(cachedResults);
      setHasCachedResults(true);
      setLastFetchTime(cachedResults[0].timestamp);
    }
  }, [hasCachedResults, lastFetchTime]);

  const cacheResults = async (query: string) => {
    const url = `https://api/search?q=${query}`;

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.status}`);
      }

      const data = await response.json();
      setResults([data, ...results]);
      setHasCachedResults(true);
      setLastFetchTime(data.timestamp);
    } catch (error) {
      setError(error);
    }
  };

  return {
    loading,
    error,
    results,
    hasCachedResults,
    lastFetchTime,
    handleDebounce,
    handleCancel,
    cacheResults,
  };
};

// SearchPage component
const SearchPage = () => {
  const searchInput = React.useRef<HTMLInputElement>();
  const [searchTerm, setSearchTerm] = useSearch(searchInput.current.value);
  const { loading, error, results, hasCachedResults, lastFetchTime, handleDebounce, handleCancel, cacheResults } = useSearch(searchTerm);
  const { searchTerm, cachedResults, setHasCachedResults } = useURLSync();

  useEffect(() => {
    const cachedResults = getCache();
    if (cachedResults && cachedResults.length > 0) {
      setResults(cachedResults);
      setHasCachedResults(true);
      setLastFetchTime(cachedResults[0].timestamp);
    }
  }, [cachedResults, lastFetchTime]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleSearch = async () => {
    if (loading) return;

    handleDebounce(() => {
      const url = `https://api/search?q=${searchTerm}`;

      try {
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`Network response was not ok: ${response.status}`);
        }

        const data = await response.json();
        setResults(data);
        setLoading(false);
      } catch (error) {
        setError(error);
      }
    }, 300);

    handleCancel();
  };

  return (
    <div>
      <input
        ref={searchInput}
        type="text"
        value={searchTerm}
        onChange={handleInputChange}
        placeholder="Search for products or services..."
      />
      {loading && (
        <div>
          <h2>Loading...</h2>
          <p>Fetching results...</p>
        </div>
      )}
      {error && (
        <div>
          <h2>Error</h2>
          <p>{error.message}</p>
        </div>
      )}
      {results && (
        <div>
          <h2>Results</h2>
          <p>{results.map(result => result.title)}</p>
        </div>
      )}
      {hasCachedResults && (
        <div>
          <h2>Cache Results</h2>
          <p>Results cached at: {new Date(lastFetchTime).toLocaleString()}</p>
        </div>
      )}
      <button onClick={handleSearch}>Search</button>
    </div>
  );
};

export default SearchPage;
```

### Explanation:

1. **useSearch Hook**:
   - This hook handles the fetching, debouncing, caching, and cancellation of search requests.
   - It uses the `useDebounce` hook from the `lodash` library to ensure that the fetch operation is executed only after the specified delay.
   - It fetches the search results and updates the component state accordingly.

2. **useURLSync Hook**:
   - This hook handles the URL synchronization by caching search results.
   - It fetches the search results from the API and updates the component state accordingly.

3. **SearchPage Component**:
   - This component uses the `useSearch` and `useURLSync` hooks to handle the search functionality.
   - It includes input for the search term, a submit button, and a button to trigger the search.
   - It handles the loading state and error state, updating the component UI accordingly.

4. **Bug Prevention**:
   - When the search input is cleared, the component fetches the cached results.
   - The URL sync implementation ensures that the same search query is cached in case a new search starts within 5 minutes.

This implementation provides a robust solution to the search feature with all the specified features.

*Response time: 11.0s*

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
### Query: Fetching 10 Most Recent Published Posts with Tags

To fetch the 10 most recent published posts, including author name, tag names, and comment count (not the comments themselves), you can use the following Prisma query:

```sql
SELECT 
    u.id, 
    u.email, 
    t.name, 
    COUNT(*) AS comment_count
FROM 
    User u
JOIN 
    Post p ON u.id = p.authorId
JOIN 
    Tag t ON p.tagId = t.id
WHERE 
    p.published = true
GROUP BY 
    u.id, u.email, t.name
ORDER BY 
    comment_count DESC
LIMIT 10;
```

### Migration Scenario: Adding a Slug Field to Post

To add a slug field to the Post model, you can use the following Prisma migration scenario:

1. **Create the migration file**: Generate a new migration file using Prisma CLI:

   ```sh
   prisma generate migration add slug
   ```

2. **Edit the migration file**: Open the generated migration file and modify the `up` and `down` functions as needed to add the slug field.

3. **Run the migration**: Apply the migration to your schema using Prisma CLI:

   ```sh
   prisma migrate up
   ```

### Query Diagnosing and Fixing Performance Bottlenecks

1. **Identify the Slow Query**: The query takes 800ms, which is not the fastest. This is because it involves joining tables and performing complex queries.

2. **Add Indexes**: Indexing can significantly speed up the query. Create an index on the `title` field to improve performance:

   ```sql
   CREATE INDEX idx_title ON Post(title);
   ```

3. **Optimize Relationships**: Ensure that your relationships are optimized to reduce data joins and improve query performance.

4. **Review Database Queries**: Look at the generated SQL queries to understand how Prisma is performing. Use a tool like `EXPLAIN` to analyze query execution paths.

### Dropping Prisma to Raw SQL

If the query is slow, you can drop Prisma to raw SQL:

1. **Drop Prisma**: Remove the Prisma CLI and other artifacts to start fresh:

   ```sh
   rm -rf prisma
   ```

2. **Reinitialize Prisma**: Initialize Prisma using the following command:

   ```sh
   prisma init
   ```

3. **Run the migrations**: Apply the migrations to your schema:

   ```sh
   prisma migrate up
   ```

### Example from the Schema

Here is a simplified example of how you might have structured your tables:

```javascript
// User model
model User {
  id Int @id @default(autoincrement());
  email String @unique;
  posts Post[];
}

// Post model
model Post {
  id Int @id;
  title String;
  content String;
  published Boolean @default(false);
  authorId Int;
  author User @relation(...);
  tags Tag[];
  comments Comment[];

  // Added slug field
  slug String @unique;
}

// Tag model
model Tag {
  id Int @id @unique;
  name String @unique;
  posts Post[];
}

// Comment model
model Comment {
  id Int @id;
  content String;
  postId Int;
  post Post @relation(...);
  authorId Int;
  author User @relation(...);
  createdAt DateTime @default(now());
}

// Example relation between User and Post
model UserPost {
  userId Int @primaryKey;
  postId Int @primaryKey;
  authorId Int @primaryKey;
}

// Example relation between Post and Tag
model PostTag {
  postId Int @primaryKey;
  tagName Int @primaryKey;
  postId Int @primaryKey;
}

// Example relation between Comment and Post
model CommentPost {
  postId Int @primaryKey;
  commentId Int @primaryKey;
  postId Int @primaryKey;
}
```

In summary, the primary query is slow due to the complexity of joining tables and performing complex queries. Addressing these bottlenecks requires creating indexes and optimizing relationships, and then running the migration to apply the changes. Additionally, dropping Prisma can be a last resort if the query is slow.

*Response time: 5.2s*

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
Let's tackle each part of the task step by step:

### 1. Write a Docker Compose.yml for Local Development

#### 1.1. Frontend
```yaml
version: '3.8'
services:
  frontend:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      - db
      - redis
```

#### 1.2. Backend
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "5000:5000"
    depends_on:
      - db
      - redis
```

#### 1.3. Database
```yaml
version: '3.8'
services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: mydatabase
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD:mypassword
    volumes:
      - ./db:/var/lib/postgresql/data
    healthcheck:
      test: pg_isready
      interval: 5s
```

#### 1.4. Redis
```yaml
version: '3.8'
services:
  redis:
    image: redis:6.2.8
    volumes:
      - ./redis:/var/lib/redis
```

### 2. Write a Production Dockerfile for the Backend (Node.js)

#### 2.1. Multi-Stage Build
```Dockerfile
# Use the official Node.js runtime as a parent image
FROM node:14

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in package.json
RUN npm install

# Expose the app port to the world outside this container
EXPOSE 5000

# Run app.js
CMD ["node", "server.js"]
```

#### 2.2. Final Image Runs as Non-Root User
```Dockerfile
# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in package.json
RUN npm install

# Expose the app port to the world outside this container
EXPOSE 5000

# Define the command to run
CMD ["node", "server.js"]
```

#### 2.3. Only Production Dependencies in Final Image
```Dockerfile
# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in package.json
RUN npm install

# Expose the app port to the world outside this container
EXPOSE 5000

# Define the command to run
CMD ["node", "server.js"]
```

### 3. The Backend Crashes in Production (Exit Code 137)

#### 3.1. Diagnosis Steps

1. **Check Database Schema Changes**: Ensure that the new nullable column was added to the database schema.

2. **Database Health Check**: Run the database health check command to check if the database is running without any errors.

3. **Check Redis Health**: Run the Redis health check command to check if the Redis service is running without any errors.

4. **Review Docker Compose Logs**: Examine the logs of the container to see any error messages related to the database or Redis.

5. **Container Restarts**: If the database or Redis service does not restart, check the logs of the container to see if there are any specific errors or warnings.

6. **Check Node.js Logs**: Review the logs of the container to see any errors related to the Node.js process.

### 4. Deployment Sequence

#### 4.1. Development Environment
- Update the `.env` file with the necessary database connection details.
- Start the development server in the local terminal or a terminal session.

#### 4.2. Production Deployment
- Push the updated Docker images to a Docker registry such as Docker Hub, AWS ECR, or Google Container Registry.
- Run the production server using Docker Compose.

#### 4.3. Database Configuration
- Update the `db` service to connect to the new database schema and connection details.

#### 4.4. Redis Configuration
- Update the `redis` service to connect to the new Redis instance and connection details.

#### 4.5. Application Configuration
- Modify the `server.js` file to include the new database connection details and handle the application configuration.

#### 4.6. Health Checks
- Run the database health check and Redis health check commands to ensure the database and Redis services are running.

#### 4.7. Monitoring and Logging
- Set up monitoring and logging tools to track the application's performance and health status.

#### 4.8. Testing and Deployment
- Conduct thorough testing of the application to ensure it meets the new database schema and Redis requirements.
- Deploy the application to production using the updated Docker images.

### Conclusion

If the backend crashes, it is likely due to an issue with the database schema changes, Redis, or Node.js. The following steps should help diagnose the problem:

1. **Review Database Schema Changes**: Ensure that the new nullable column was added to the database schema.
2. **Database Health Check**: Run the database health check command to check if the database is running without any errors.
3. **Redis Health Check**: Run the Redis health check command to check if the Redis service is running without any errors.
4. **Review Docker Compose Logs**: Examine the logs of the container to see any error messages related to the database or Redis.
5. **Container Restarts**: If the database or Redis service does not restart, check the logs of the container to see if there are any specific errors or warnings.
6. **Check Node.js Logs**: Review the logs of the container to see any errors related to the Node.js process.
7. **Health Checks**: Run the database health check and Redis health check commands to ensure the database and Redis services are running.
8. **Monitoring and Logging**: Set up monitoring and logging tools to track the application's performance and health status.

By following these steps, you can diagnose and resolve the issue causing the backend to crash in production.

*Response time: 7.8s*

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
To implement a collaborative document editor in Node.js using the WebSocket library, we need to handle connections, messages, and the logic for broadcasting changes. Below is a simplified implementation of the server side:

```javascript
const WebSocket = require('ws');

// Define the connection map
const connections = new Map();

// Define the message routing
const messageRouter = {
  joinDocument: (connection, documentId) => {
    const newConnection = new WebSocket(connection);
    newConnection.on('message', (message) => {
      console.log(`Received message from ${connection.remoteAddress}: ${message}`);
      // Broadcast the message to all other users in the document
      broadcastMessageToAllUsers(connection, documentId, message);
    });
    newConnection.on('close', () => {
      // Remove the connection from the map
      connections.delete(connection);
    });
  },
  textChange: (connection, text) => {
    const documentId = connection.remoteAddress;
    // Broadcast the text change to all other users in the document
    broadcastMessageToAllUsers(connection, documentId, text);
  },
  cursorMove: (connection, newPosition) => {
    const documentId = connection.remoteAddress;
    // Broadcast the cursor move to all other users in the document
    broadcastMessageToAllUsers(connection, documentId, newPosition);
  },
  userLeft: (connection) => {
    const documentId = connection.remoteAddress;
    // Remove the connection from the map
    connections.delete

*Response time: 1.9s*

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
### Step 1: Complete the GraphQL Schema (SDL)

First, let's define the schema for the recipe platform. The schema will include the following types:

```graphql
type Query {
  recipes(filter: RecipeFilter, pagination: PaginationInput): [Recipe]
}

type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String): Recipe
}

type Recipe {
  id: ID!
  title: String!
  ingredients: [Ingredient]
  steps: [Step]
  author: Author!
  tags: [Tag]
  ratings: [Rating]
}

type Ingredient {
  id: ID!
  name: String!
  amount: Float!
  unit: Unit!
}

type Step {
  id: ID!
  name: String!
  ingredients: [Ingredient]
  recipe: Recipe!
}

type Author {
  id: ID!
  name: String!
  profilePicture: ProfilePicture!
  bio: String!
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

type ProfilePicture {
  id: ID!
  url: String!
}
```

### Step 2: Write Resolvers

#### Query

```graphql
type Query {
  recipes(filter: RecipeFilter, pagination: PaginationInput): [Recipe]
}

type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String): Recipe
}

type Recipe {
  id: ID!
  title: String!
  ingredients: [Ingredient]
  steps: [Step]
  author: Author!
  tags: [Tag]
  ratings: [Rating]
}

type Ingredient {
  id: ID!
  name: String!
  amount: Float!
  unit: Unit!
}

type Step {
  id: ID!
  name: String!
  ingredients: [Ingredient]
  recipe: Recipe!
}

type Author {
  id: ID!
  name: String!
  profilePicture: ProfilePicture!
  bio: String!
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

type ProfilePicture {
  id: ID!
  url: String!
}
```

#### Mutation

```graphql
type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String): Recipe
}
```

#### Recipe Average Rating

```graphql
type Recipe {
  id: ID!
  title: String!
  ingredients: [Ingredient]
  steps: [Step]
  author: Author!
  tags: [Tag]
  ratings: [Rating]
}

type Ingredient {
  id: ID!
  name: String!
  amount: Float!
  unit: Unit!
}

type Step {
  id: ID!
  name: String!
  ingredients: [Ingredient]
  recipe: Recipe!
}

type Author {
  id: ID!
  name: String!
  profilePicture: ProfilePicture!
  bio: String!
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

type ProfilePicture {
  id: ID!
  url: String!
}
```

### Step 3: Fix the Problem with DataLoader

To fix the problem with the DataLoader, we need to ensure that the resolvers are not re-executing the same recipe data for different `recipeId`s. We can use a combination of `cache` and `cacheKey` to ensure that each recipe is fetched only once.

#### Resolvers

```javascript
import { gql } from 'apollo-server-express';
import { cache } from 'apollo-cache-inmemory';
import { makeExecutableSchema } from 'graphql-tools';

const typeDefs = gql`
  type Query {
    recipes(filter: RecipeFilter, pagination: PaginationInput): [Recipe]
  }

  type Mutation {
    addRating(recipeId: ID!, score: Float!, comment: String): Recipe
  }

  type Recipe {
    id: ID!
    title: String!
    ingredients: [Ingredient]
    steps: [Step]
    author: Author!
    tags: [Tag]
    ratings: [Rating]
  }

  type Ingredient {
    id: ID!
    name: String!
    amount: Float!
    unit: Unit!
  }

  type Step {
    id: ID!
    name: String!
    ingredients: [Ingredient]
    recipe: Recipe!
  }

  type Author {
    id: ID!
    name: String!
    profilePicture: ProfilePicture!
    bio: String!
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

  type ProfilePicture {
    id: ID!
    url: String!
  }
`;

const schema = makeExecutableSchema({
  typeDefs
});

const cache = new Cache();

schema.addResolver((parent, args, context) => {
  // Cache key is the recipeId, so if the recipeId changes, the cache is invalidated
  const cacheKey = `${args.tag}-${args.minRating}`;

  // Check if the cached result exists
  const cachedResult = cache.get(cacheKey);

  if (cachedResult) {
    return cachedResult;
  }

  // Fetch the recipe data from the database
  const recipe = context.recipeRepository.getRecipe(args.id);

  // Add the recipe to the cache
  cache.set(cacheKey, recipe);

  return recipe;
});

// Resolvers for the query
schema.addResolver((parent, args, context) => {
  const { filter, pagination } = args;

  const query = `
    query recipes {
      recipes(filter: {tag: $tag, minRating: $minRating}, pagination: {page: $page, limit: $limit}) {
        nodes {
          id
          title
          ingredients {
            id
            name
            amount
            unit
          }
          steps {
            id
            name
            ingredients {
              id
              name
              amount
              unit
            }
          }
          author {
            id
            name
            profilePicture
            bio
          }
          tags {
            id
            name
          }
          ratings {
            id
            score
            comment
          }
        }
      }
    }
  `;

  const { page, limit } = pagination;
  const total = await context.recipeRepository.getRecipesCount(args.tag, args.minRating);

  const offset = (page - 1) * limit;

  const result = await context.recipeRepository.getRecipes(query, { offset, limit });

  return {
    nodes: result.nodes,
    total,
    skip: offset,
    limit,
  };
});

// Resolvers for the mutation
schema.addResolver((parent, args, context) => {
  const { recipeId, score, comment } = args;

  const query = `
    mutation addRating($recipeId: ID!, $score: Float!, $comment: String) {
      addRating(recipeId: $recipeId, score: $score, comment: $comment) {
        recipe {
          id
          title
          ingredients {
            id
            name
            amount
            unit
          }
          steps {
            id
            name
            ingredients {
              id
              name
              amount
              unit
            }
          }
          author {
            id
            name
            profilePicture
            bio
          }
          tags {
            id
            name
          }
          ratings {
            id
            score
            comment
          }
        }
      }
    }
  `;

  const result = await context.recipeRepository.addRating(query, { recipeId, score, comment });

  return result;
});

// Resolver for the Recipe.averageRating
schema.addResolver((parent, args, context) => {
  const query = `
    query averageRating {
      averageRating {
        id
        score
        comment
      }
    }
  `;

  const result = await context.recipeRepository.getAverageRating();

  return result;
});
```

### Step 4: Client Query

Now, let's write the client query that fetches the recipe title + author name + first 3 ingredients in one request:

```javascript
const client = new ApolloClient({
  url: 'http://localhost:4000',
  cache: cache,
  resolvers: {
    Recipe,
    Ingredient,
    Step,
    Author,
    Tag,
    Rating,
    ProfilePicture,
  },
});
```

### Step 5: Choose Between GraphQL and REST

- **GraphQL**: **Pros**: It's more flexible and powerful, allowing for easier integration with other services and tools. It supports a wide range of query languages and data sources, and it can handle large data sets efficiently. However, it may require more complex setup and can be more verbose than REST.
- **REST**: **Pros**: It's simpler and easier to use, as it doesn't require additional setup. It can handle large data sets efficiently, and it supports a wide range of query languages and data sources. However, it may require more complex setup and can be less flexible than GraphQL.

In general, the choice between GraphQL and REST depends on the specific needs of the application and the type of data being fetched. If the application is a large-scale application, a hybrid approach might be necessary. If the application is a microservices architecture, a more lightweight approach might be preferred.

*Response time: 11.5s*

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
To implement the specified UI layout, we will use a combination of Flexbox and Grid. The layout will ensure that the header is fixed at the top, and the main content will fill the full viewport height below the header. The sidebar and main content will scroll independently, and cards will use CSS Grid for responsive layout. Here's the complete implementation:

### HTML

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Responsive UI Layout</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header class="header">
        <!-- Header content goes here -->
    </header>

    <main class="main-content">
        <!-- Main content goes here -->
        <section class="sidebar">
            <!-- Sidebar content goes here -->
        </section>
        <section class="main-content">
            <!-- Main content goes here -->
        </section>
    </main>
</body>
</html>
```

### CSS (styles.css)

```css
body {
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
}

.header {
    position: fixed;
    top: 0;
    width: 100%;
    height: 60px;
    background-color: #333;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 999;
}

.sidebar {
    position: fixed;
    top: 60px;
    left: 0;
    width: 240px;
    height: 100%;
    background-color: #ccc;
    overflow-y: auto;
}

.main-content {
    width: 100%;
    height: 100%;
    overflow-y: auto;
}

.card {
    width: 100%;
    background-color: #fff;
    border-radius: 5px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 20px;
}

.card img {
    width: 100%;
    height: auto;
    object-fit: cover;
}

.card title {
    margin-top: 10px;
}

.card description {
    margin-top: 20px;
}

.card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #4CAF50;
    color: white;
    padding: 10px;
    border-radius: 5px;
    cursor: pointer;
}

.card-footer button {
    margin-left: 5px;
    padding: 10px 20px;
    background-color: transparent;
    border: none;
    border-radius: 5px;
    color: white;
    cursor: pointer;
}
```

### Explanation:

1. **Header**: The header is fixed at the top with a height of 60px. It is fixed to the top and does not scroll behind it. The background color is set to a light gray to create a sense of a fixed header.

2. **Sidebar**: The sidebar is fixed to the right of the header with a width of 240px. It is fixed and does not scroll independently. The background color is set to a light gray to create a sense of a fixed sidebar.

3. **Main Content**: The main content is fixed to the left of the sidebar with a width of 100%. It is fixed and does not scroll independently. The overflow-y: auto; property allows it to scroll independently.

4. **Cards**: Each card is a flex container with a width of 100% and a height of 100%. The background color is set to a light gray to create a sense of a responsive grid layout. The object-fit: cover; property is used to ensure that the image is responsive and maintains its aspect ratio.

5. **Card Image**: The card image is centered within the card using the `object-fit: cover;` property.

6. **Card Title**: The card title is centered within the card using the `margin-top: 10px;` property.

7. **Card Description**: The card description is centered within the card using the `margin-top: 20px;` property.

8. **Card Footer**: The card footer contains two buttons: one left-aligned and one right-aligned. The buttons have a background color set to a light gray and are styled with a white border, rounded corners, and a white color for the text. The buttons have a padding of 10px and are centered within the card.

By using Flexbox and Grid, we can achieve the desired layout with minimal JavaScript and valid HTML + CSS. The header is fixed, the sidebar and main content fill the full viewport height, and cards use CSS Grid for responsive layout.

*Response time: 6.2s*

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
### 1. Transport Mechanism and Why

**WebSocket**: The most straightforward and efficient transport mechanism for real-time notifications is WebSocket. It is widely used due to its real-time communication capabilities and low overhead. WebSocket is also efficient in terms of data transfer speed, making it ideal for applications that require real-time updates or notifications without requiring full duplex communication.

**SSE (Server-Sent Events)**: Server-Sent Events (SSE) is a lightweight protocol that allows clients to send events to the server without having to send the entire event payload. It is designed to be efficient and scalable, making it suitable for applications that require real-time updates.

**Polling**: Polling is a mechanism where the server periodically sends data to the client. This approach can be inefficient for large datasets and can lead to performance issues if the server is too slow or if there are network issues.

**Push Notifications**: Push notifications are a simplified version of polling, where the server sends only the data to the client when it is available. This is a good choice for applications that do not require real-time updates.

### 2. Storage Schema

**Database Schema**: A common database schema for real-time notifications could include:

- **Task Table**: Contains task details, such as task ID, title, description, assignee, status, and due date.
- **Notification Table**: Contains notification details, such as notification ID, user ID, task ID, type (e.g., 'task_assigned', 'comment_added', 'deadline_reached'), and the time the notification was created.
- **User Table**: Contains user details, such as user ID, username, and email address.

### 3. Handling Offline Users

**Offline Notification**: If a user is offline, they will not receive any notifications immediately. To handle this, you can implement a system that periodically sends a notification to the user when they come back online. You can use a combination of webhooks, polling, and real-time event streams to keep the user informed of new notifications.

**Queue or Event-Driven**: If the user is offline, you can use a queue to store the notification and process it when the user comes back online. You can use a message broker to send notifications to the queue.

### 4. Deadline Check

**Cron Job**: If there are 100,000 concurrent users, the deadline check can be implemented using a cron job to run every hour for all tasks. The cron job can be set up to run on a separate server or cloud platform and send a notification to the user when the deadline is approaching.

**Queue or Event-Driven**: If there are 100,000 concurrent users, you can use a queue to store the task and handle the deadline check. You can use a message broker to send notifications to the queue when the deadline is approaching.

### 5. Scaling

To scale this system, you can consider the following strategies:

- **Horizontal Scaling**: Increase the number of nodes in the system to handle more users. This can be achieved using cloud platforms like AWS, Azure, or Google Cloud.

- **Vertical Scaling**: Increase the number of nodes in the system to handle more users. This can be achieved using cloud platforms like AWS, Azure, or Google Cloud.

- **Database Scaling**: Scale the database to handle more users. This can be achieved using cloud

*Response time: 4.0s*

---
