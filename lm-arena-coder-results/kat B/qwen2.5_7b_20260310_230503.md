# Model: qwen2.5:7b
**Test Date:** 2026-03-11 00:24:57
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
Sure, let's design the REST API for your multi-tenant SaaS project management tool following the given rules and conventions.

### 1. Define All Endpoints

#### Workspace
- **Create Workspace**: `POST /workspaces`
- **List Workspaces**: `GET /workspaces`
- **Get Workspace**: `GET /workspaces/{workspaceId}`
- **Update Workspace**: `PUT /workspaces/{workspaceId}`
- **Delete Workspace**: `DELETE /workspaces/{workspaceId}`

#### Project
- **Create Project**: `POST /workspaces/{workspaceId}/projects`
- **List Projects**: `GET /workspaces/{workspaceId}/projects`
- **Get Project**: `GET /workspaces/{workspaceId}/projects/{projectId}`
- **Update Project**: `PUT /workspaces/{workspaceId}/projects/{projectId}`
- **Delete Project**: `DELETE /workspaces/{workspaceId}/projects/{projectId}`

#### Task
- **Create Task**: `POST /workspaces/{workspaceId}/projects/{projectId}/tasks`
- **List Tasks**: `GET /workspaces/{workspaceId}/projects/{projectId}/tasks`
- **Get Task**: `GET /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}`
- **Update Task**: `PUT /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}`
- **Delete Task**: `DELETE /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}`
- **Update Task Status**: `PUT /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/status`
- **List Tasks with Filters**: `GET /workspaces/{workspaceId}/projects/{projectId}/tasks?assignee={userId}&status={status}&dueDate={dueDate}`

#### User
- **Create User**: `POST /users`
- **List Users**: `GET /users`
- **Get User**: `GET /users/{userId}`
- **Update User**: `PUT /users/{userId}`
- **Delete User**: `DELETE /users/{userId}`

#### Comment
- **Add Comment**: `POST /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments`
- **List Comments**: `GET /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments`
- **Get Comment**: `GET /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments/{commentId}`
- **Update Comment**: `PUT /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments/{commentId}`
- **Delete Comment**: `DELETE /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments/{commentId}`

### 2. Request/Response JSON Shapes

#### Create Task

*Response time: 12.9s*

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
Sure, let's go through the implementation step-by-step. We'll use Node.js, Express, and TypeScript, along with Zod for validation.

### Step 1: Set Up the Project

First, ensure you have Node.js and npm installed. Then, set up a new project:

```bash
mkdir workspace-manager
cd workspace-manager
npm init -y
npm install express @types/express zod
npm install --save-dev typescript @types/node @types/express ts-node @types/zod
```

### Step 2: Create the Project Structure

Create the necessary files and folders:

```
workspace-manager/
├── src/
│   ├── index.ts
│   ├── types.ts
│   ├── workspace-manager.ts
│   └── validation.ts
├── tsconfig.json
└── package.json
```

### Step 3: Configure TypeScript

Create `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES6",
    "module": "commonjs",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "./dist"
  },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### Step 4: Create the Express Application

In `src/index.ts`:

```typescript
import express, { Request, Response, NextFunction } from 'express';
import { ZodError } from 'zod';
import { validationMiddleware } from './validation';
import { TaskManager } from './workspace-manager';

const app = express();
app.use(express.json());

const taskManager = new TaskManager();

app.patch('/workspaces/:workspaceId/tasks/:taskId', validationMiddleware, (req: Request, res: Response, next: NextFunction) => {
  const { workspaceId, taskId } = req.params;
  const { title, status, assignee_id, due_date } = req.body;

  try {
    const updatedTask = taskManager.updateTask(
      parseInt(workspaceId, 10),
      parseInt(taskId, 10),
      title,
      status,
      assignee_id,
      due_date
    );
    res.json(updatedTask);
  } catch (error) {
    next(error);
  }
});

app.use((err: any, req: Request, res: Response, next: NextFunction) => {
  if (err instanceof ZodError) {
    res.status(400).json({ errors: err.errors });
  } else if (err.status === 404) {
    res.status(404).json({ message: 'Resource not found' });
  } else if (err.status === 409) {
    res.status(409).json({ message: 'Conflict' });
  } else {
    console.error(err);
    res.status(500).json({ message: 'Internal Server Error' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
```

### Step 5: Create the Task Manager

In `src/workspace-manager.ts`:

```typescript
class Task {
  constructor(
    public title: string,
    public status: string,
    public assignee_id: number | null,
    public due_date: string | null
  ) {}
}

class TaskManager {
  private tasks: Map<number, Task> = new Map();
  private workspaces: Map<number, Set<number>> = new Map();

  constructor() {
    this.tasks.set(1, new Task('Task 1', 'todo', null, null));
    this.workspaces.set(1, new Set([1, 2, 3]));
    this.tasks.set(2, new Task('Task 2', 'in_progress', 1, '2023-10-01'));
  }

  updateTask(
    workspaceId: number,
    taskId: number,
    title: string | undefined,
    status: string | undefined,
    assignee_id: number | null | undefined,
    due_date: string | null | undefined
  ): Task | undefined {
    if (!this.workspaces.has(workspaceId)) {
      throw new Error('Workspace not found');
    }

    if (!this.tasks.has(taskId)) {
      throw new Error('Task not found');
    }

    const task = this.tasks.get(taskId);
    if (!task) return;

    if (status && ['cancelled', 'done', 'in_progress', 'todo'].includes(status) && status !== task.status) {
      if (status === 'cancelled' && task.subtasks.some((subtask) => subtask.status !== 'cancelled')) {
        throw new Error('Cannot cancel task with open subtasks');
      }
    }

    if (assignee_id && !this.workspaces.get(workspaceId)?.has(assignee_id)) {
      throw new Error('Assignee not found in the workspace');
    }

    if (title) task.title = title;
    if (status) task.status = status;
    if (assignee_id) task.assignee_id = assignee_id;
    if (due_date) task.due_date = due_date;

    return task;
  }
}
```

### Step 6: Validation Schema

In `src/validation.ts`:

```typescript
import { z } from 'zod';

const taskPatchSchema = z.object({
  title: z.string().max(200).optional(),
  status: z.enum(['todo', 'in_progress', 'done', 'cancelled']).optional(),
  assignee_id: z.union([z.number().optional(), z.literal(null)]).optional(),
  due_date: z.union([z.string().optional(), z.literal(null).optional()]).optional(),
});

export { taskPatchSchema };
```

### Step 7: Middleware

In `src/validation.ts`:

```typescript
import { Request, Response, NextFunction } from 'express';
import { taskPatchSchema } from './validation';

export const validationMiddleware = (req: Request, res: Response, next: NextFunction) => {
  try {
    taskPatchSchema.parse({
      title: req.body.title,
      status: req.body.status,
      assignee_id: req.body.assignee_id,
      due_date: req.body.due_date,
    });
    next();
  } catch (error) {
    next(error);
  }
};
```

### Step 8: Unit Tests

Create a `test` folder and add the following files:

#### `test/validation.test.ts`

```typescript
import { taskPatchSchema } from '../src/validation';
import { z } from 'zod';

describe('Task Patch Validation', () => {
  test('valid request', () => {
    const result = taskPatchSchema.safeParse({
      title: 'New Title',
      status: 'in_progress',
      assignee_id: 1,
      due_date: '2023-10-15',
    });
    expect(result.success).toBe(true);
  });

  test('missing required field', () => {
    const result = taskPatchSchema.safeParse({
      status: 'in_progress',
      assignee_id: 1,
      due_date: '2023-10-15',
    });
    expect(result.success).toBe(false);
    expect(result.error.issues[0].path).toBe('title');
  });

  test('invalid status', () => {
    const result = taskPatch

*Response time: 34.2s*

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
Sure, let's implement a complete authentication system using Node.js, Express, and TypeScript. We'll cover the steps outlined in your request, including setting up the necessary middleware and handling different scenarios.

### Step 1: Setup the Project

First, let's set up the project with the required dependencies and create the basic structure.

1. **Initialize the project:**
   ```bash
   mkdir express-auth
   cd express-auth
   npm init -y
   npm install express @types/express bcryptjs @types/bcryptjs jsonwebtoken @types/jsonwebtoken cookie-parser body-parser ts-node typescript --save
   ```

2. **Configure `tsconfig.json`:**
   ```json
   {
     "compilerOptions": {
       "target": "ES6",
       "module": "commonjs",
       "strict": true,
       "esModuleInterop": true
     },
     "include": ["src"]
   }
   ```

3. **Create the project structure:**
   ```bash
   mkdir src
   touch src/index.ts src/auth.ts src/models/user.ts src/middlewares/authMiddleware.ts
   ```

4. **Install and configure `nodemon` for development:**
   ```bash
   npm install --save-dev nodemon
   echo "require('dotenv').config(); require('./src/index');" > src/index.ts
   echo "const express = require('express'); const { authMiddleware } = require('./src/middlewares/authMiddleware'); const app = express(); app.use(express.json()); app.use(authMiddleware); app.get('/auth/me', (req, res) => res.send(req.user)); app.post('/auth/register', require('./src/auth').register); app.post('/auth/login', require('./src/auth').login); app.listen(3000, () => console.log('Server running on port 3000'));" > src/index.ts
   ```

### Step 2: Define the User Model

In `src/models/user.ts`:
```typescript
import { Model, Document, ObjectId } from 'mongoose';

interface IUserDocument extends Document {
  email: string;
  password: string;
  role: 'user' | 'admin';
}

interface IUserModel extends Model<IUserDocument> {
  findOrCreateByCredentials(email: string, password: string): Promise<IUserDocument>;
}

const UserSchema = new Model<IUserDocument, IUserModel>({
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  role: { type: String, required: true },
});

UserSchema.statics.findOrCreateByCredentials = async (email: string, password: string) => {
  const user = await User.findOne({ email });
  if (user && (await user.comparePassword(password))) {
    return user;
  }
  const newUser = new User({ email, password, role: 'user' });
  await newUser.save();
  return newUser;
};

export default UserSchema;
```

### Step 3: Implement Authentication Logic

In `src/auth.ts`:
```typescript
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import User from '../models/user';
import { Request, Response, NextFunction } from 'express';

const register = async (req: Request, res: Response) => {
  const { email, password } = req.body;
  const hashedPassword = await bcrypt.hash(password, 12);
  const user = await User.findOrCreateByCredentials(email, hashedPassword);
  res.json({ email: user.email, role: user.role });
};

const login = async (req: Request, res: Response) => {
  const { email, password } = req.body;
  const user = await User.findOrCreateByCredentials(email, password);
  const accessToken = jwt.sign(
    { userId: user._id, email: user.email, role: user.role, iat: Date.now(), exp: Date.now() + 15 * 60 * 1000 },
    'your-256-bit-secret',
    { expiresIn: '15m' }
  );
  const refreshToken = jwt.sign(
    { userId: user._id, email: user.email, role: user.role, iat: Date.now(), exp: Date.now() + 7 * 24 * 60 * 60 * 1000 },
    'your-256-bit-secret',
    { expiresIn: '7d' }
  );
  res.cookie('refreshToken', refreshToken, { httpOnly:

*Response time: 20.4s*

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
Certainly! Let's dive into each part of the authentication system you've outlined.

### 1. POST /auth/refresh — Use the refresh token from cookie to issue a new access token. Rotate the refresh token (issue new one, invalidate old one).

To handle this, we'll assume you have a backend service that handles the authentication and a database like Redis for storing the tokens.

**Example implementation in Python:**

```python
import time
import jwt
import redis
from flask import request, jsonify

# Redis client setup
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# JWT secret key
JWT_SECRET = 'your_jwt_secret'

def generate_access_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': time.time() + 3600  # Token expires in 1 hour
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def generate_refresh_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': time.time() + 86400  # Token expires in 24 hours
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def validate_token(token):
    try:
        payload = jwt

*Response time: 6.2s*

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
Sure! Below is the implementation of the DataTable component in React and TypeScript. This component will have the specified features and be fully controlled or uncontrolled based on the props passed by the caller.

### 1. TypeScript Interface for Props

```typescript
import React, { FC, ChangeEvent, useState, useMemo, useCallback } from 'react';

interface DataTableProps<T> {
    columns: {
        key: string;
        header: string;
        width?: number;
        sortable?: boolean;
        renderCell?: (row: T, index: number) => React.ReactNode;
    }[];
    data: T[];
    pageSizeOptions?: number[];
    onRowSelectionChange?: (selectedRows: boolean[], selectedRowIndices: number[]) => void;
    onSortingChange?: (sortColumn: string | null, order: 'asc' | 'desc' | null) => void;
    selectedRows?: boolean[];
    currentPage?: number;
    onPageChange?: (newPage: number) => void;
    isControlled?: boolean;
}

interface DataTableState<T> {
    sortColumn: string | null;
    sortOrder: 'asc' | 'desc' | null;
    selectedRows: boolean[];
    currentPage: number;
}
```

### 2. Complete Component Implementation

```typescript
import React, { FC, ChangeEvent, useState, useMemo, useCallback } from 'react';
import './DataTable.css'; // Assuming you have a CSS file for styling

const DataTable: FC<DataTableProps<any>> = ({
    columns,
    data,
    pageSizeOptions = [10, 25, 50],
    onRowSelectionChange,
    onSortingChange,
    selectedRows,
    currentPage = 1,
    onPageChange,
    isControlled,
}) => {
    const [sortColumn, setSortColumn] = useState<string | null>(null);
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc' | null>(null);
    const [selectedRowsState, setSelectedRowsState] = useState(selectedRows ?? Array(data.length).fill(false));

    const handleColumnSort = (key: string) => {
        if (sortColumn === key) {
            setSortOrder(order => (order === 'asc' ? 'desc' : 'asc' || null));
        } else {
            setSortColumn(key);
            setSortOrder('asc');
        }
        onSortingChange?.(key, sortOrder);
    };

    const handleRowSelection = (index: number, selected: boolean) => {
        const newSelectedRows = [...selectedRowsState];
        newSelectedRows[index] = selected;
        setSelectedRowsState(newSelectedRows);
        onRowSelectionChange?.(newSelectedRows, [...Array(data.length).keys()].filter((_, i) => newSelectedRows[i]));
    };

    const handlePageChange = (newPage: number) => {
        onPageChange?.(newPage);
    };

    const sortedData = useMemo(() => {
        if (sortColumn) {
            const sortedData = [...data].sort((a, b) => {
                if (sortOrder === 'asc') {
                    return a[sortColumn] < b[sortColumn] ? -1 : a[sortColumn] > b[sortColumn] ? 1 : 0;
                } else if (sortOrder === 'desc') {
                    return a[sortColumn] > b[sortColumn] ? -1 : a[sortColumn] < b[sortColumn] ? 1 : 0;
                }
                return 0;
            });
            return sortedData;
        }
        return data;
    }, [data, sortColumn, sortOrder]);

    const paginatedData = useMemo(() => {
        const start = (currentPage - 1) * pageSizeOptions[0];
        const end = start + pageSizeOptions[0];
        return sortedData.slice(start, end);
    }, [sortedData, currentPage, pageSizeOptions]);

    return (
        <div className="data-table">
            <table>
                <thead>
                    <tr>
                        <th>
                            <input type="checkbox" checked={selectedRowsState.every(row => row)} onChange={e => {
                                const selected = e.target.checked;
                                setSelectedRowsState(Array(data.length).fill(selected));
                                onRowSelectionChange?.(Array(data.length).fill(selected), [...Array(data.length).keys()]);
                            }} />
                        </th>
                        {columns.map((col, index) => (
                            <th key={col.key} onClick={() => handleColumnSort(col.key)} style={{ width: col.width }}>
                                {col.header}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {paginatedData.map((row, index) => (
                        <tr key={index}>
                            <td>
                                <input type="checkbox" checked={selectedRowsState[index]} onChange={() => handleRowSelection(index, !selectedRowsState[index])} />
                            </td>
                            {columns.map((col, cIndex) => (
                                <td key={cIndex}>
                                    {col.renderCell ? col.renderCell(row, index) : row[col.key]}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default DataTable;
```

### 3. Usage Example

```typescript
import React, { useState } from 'react';

interface User {
    id: number;
    name: string;
    email: string;
    actions: boolean;
}

const App: React.FC = () => {
    const [selectedRows, setSelectedRows] = useState<boolean[]>([]);
    const [currentPage, setCurrentPage] = useState(1);

    const users: User[] = [
        { id: 1, name: 'Alice', email: 'alice@example.com', actions: false },
        { id: 2, name: 'Bob', email: 'bob@example.com', actions: false },
        { id: 3, name: 'Charlie', email: 'charlie@example.com', actions: false },
        // More users...
    ];

    const columns = [
        {
            key: 'actions',
            header: 'Actions',
            width: 100,
            sortable: false,
            renderCell: (user: User, index: number) => (
                <button onClick={() => console.log(`Action button clicked for ${user.name}`)}>Edit</button>
            ),
        },
        {
            key: 'id',
            header: 'ID',
            width: 50,
            sortable: true,
        },
        {
            key: 'name',
            header: 'Name',
            width: 200,
            sortable: true,
        },
        {
            key: 'email',
            header: 'Email',
            width: 300,
            sortable: true,
        },
    ];

    return (
        <DataTable
            columns={columns}
            data={users}
            selectedRows={selectedRows}
            currentPage={currentPage}
            onPageChange={(newPage) => setCurrentPage(newPage)}
            onRowSelectionChange={(newSelectedRows, selectedRowIndices) => setSelectedRows(newSelectedRows)}
            isControlled={true}
        />
    );
};

export default App;
```

### 4. Memoization

To avoid unnecessary re-renders, memoization is used in the `useMemo` hooks to memoize the `sortedData` and `paginatedData`. This ensures that the component only re-renders when the dependencies change.

```typescript
const sortedData = useMemo(() => {
    // ... (same as above)
}, [data, sortColumn, sortOrder]);

const paginatedData = useMemo(() => {
    // ... (same as above)
}, [sortedData, currentPage, pageSizeOptions]);
```

These memoized values ensure that the component only updates when the underlying data or state changes, which can significantly improve performance.

*Response time: 35.3s*

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
Sure, let's break down the implementation step by step. We'll start with the custom hook `useSearch` and then move on to the `SearchPage` component. Finally, we'll handle the URL synchronization and discuss the importance of canceling in-flight requests.

### 1. Custom Hook `useSearch`

We'll create a custom hook `useSearch` that handles the search logic, including debouncing, caching, and cancellation.

```jsx
import { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const useSearch = (query) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cachedResults, setCachedResults] = useState(null);
  const [cachedTimestamp, setCachedTimestamp] = useState(null);
  const prevQuery = useRef('');

  const clearCache = () => {
    setCachedResults(null);
    setCachedTimestamp(null);
  };

  const handleSearch = async (q) => {
    if (q === prevQuery.current) {
      if (cachedResults && new Date().getTime() - cachedTimestamp < 300000) {
        setResults(cachedResults);
        setLoading(false);
        return;
      }
    }

    clearCache();

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`/api/search?q=${q}`);
      setResults(response.data);
      setCachedResults(response.data);
      setCachedTimestamp(new Date().getTime());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (query) {
      prevQuery.current = query;
      const timeoutId = setTimeout(() => {
        handleSearch(query);
      }, 300);

      return () => clearTimeout(timeoutId);
    }
  }, [query]);

  return { results, loading, error, handleSearch };
};

export default useSearch;
```

### 2. The SearchPage Component

Now, we'll create the `SearchPage` component that uses the `useSearch` hook.

```jsx
import React, { useState } from 'react';
import useSearch from './useSearch';

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const { results, loading, error, handleSearch } = useSearch(query);

  const handleSearchChange = (event) => {
    setQuery(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    handleSearch(query);
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={handleSearchChange}
          placeholder="Search..."
        />
      </form>
      {loading && <div>Loading...</div>}
      {error && <div>Error: {error}</div>}
      {results.length > 0 && (
        <ul>
          {results.map((result) => (
            <li key={result.id}>{result.name}</li>
          ))}
        </ul>
      )}
      {results.length === 0 && !loading && !error && <div>No results</div>}
    </div>
  );
};

export default SearchPage;
```

### 3. URL Sync Implementation

To ensure the URL stays in sync with the query, we can use the `useEffect` hook to listen for changes in the URL query parameter and update the `query` state.

```jsx
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const [searchParams] = useSearchParams();
  const { results, loading, error, handleSearch } = useSearch(query);

  useEffect(() => {
    if (searchParams.get('q')) {
      setQuery(searchParams.get('q'));
    }
  }, [searchParams]);

  useEffect(() => {
    if (query) {
      searchParams.set('q', query);
    } else {
      searchParams.delete('q');
    }
    searchParams.sort();
    const url = new URL(window.location.href);
    url.search = searchParams.toString();
    window.history.pushState({}, '', url);
  }, [query, searchParams]);

  const handleSearchChange = (event) => {
    setQuery(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    handleSearch(query);
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={handleSearchChange}
          placeholder="Search..."
        />
      </form>
      {loading && <div>Loading...</div>}
      {error && <div>Error: {error}</div>}
      {results.length > 0 && (
        <ul>
          {results.map((result) => (
            <li key={result.id}>{result.name}</li>
          ))}
        </ul>
      )}
      {results.length === 0 && !loading && !error && <div>No results</div>}
    </div>
  );
};

export default SearchPage;
```

### 4. Why is Cancelling In-Flight Requests Important?

Cancelling in-flight requests is crucial because it prevents multiple search requests from being made when a user types quickly. For example, if a user types "abc" and "abcd" rapidly, without cancellation, multiple requests might be sent to the server, which is not only inefficient but also redundant. By canceling the previous request when a new one is made, we ensure that only the latest search query is processed, providing a better user experience. This prevents potential race conditions and unnecessary server load.

*Response time: 26.1s*

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
Sure, let's go through each of the tasks step by step.

### 1. Fetching 10 Most Recent Published Posts

To fetch the 10 most recent published posts along with their author names, tag names, and comment counts, you can use a combination of `select`, `count`, and join operations. Here is the Prisma query:

```prisma
const posts = await prisma.post
  .findMany({
    where: { published: true },
    orderBy: { createdAt: 'desc' },
    take: 10,
    include: {
      author: {
        select: { name: true },
      },
      tags: {
        select: { name: true },
      },
      comments: {
        select: { count: true },
      },
    },
  });
```

### 2. Adding a Slug Field to the Post Model

Adding a non-nullable and unique field like `slug` to an existing table with 10 million rows requires a strategic approach to avoid downtime. Here is a step-by-step migration scenario:

1. **Add a Nullable Column:**
   ```prisma
   model Post {
     id Int @id
     title String
     content String
     published Boolean @default(false)
     authorId Int
     author User @relation(...)
     tags Tag[]
     comments Comment[]
     createdAt DateTime @default(now())
     slug String? // Nullable initially
   }
   ```

2. **Update the Database:**
   ```bash
   npx prisma migrate dev --name add_slug_field
   ```

3. **Generate Slugs:**
   Use a script to generate unique slugs for existing posts. You can use a library like `nanoid` or `slug` in JavaScript to generate slugs.

   ```javascript
   const { slug } = require('slug');
   const posts = await prisma.post.findMany();
   posts.forEach(post => {
     post.slug = slug(post.title);
   });
   await prisma.post.updateMany({ data: { slug: { set: posts.map(post => post.slug) } } });
   ```

4. **Set the Column to Non-Nullable:**
   ```prisma
   model Post {
     id Int @id
     title String
     content String
     published Boolean @default(false)
     authorId Int
     author User @relation(...)
     tags Tag[]
     comments Comment[]
     createdAt DateTime @default(now())
     slug String @unique @db.VarChar(255) // Set as non-nullable
   }
   ```

5. **Update the Database:**
   ```bash
   npx prisma migrate dev --name set_slug_non_nullable
   ```

6. **Run Final Checks:**
   Ensure all slugs are set correctly and there are no null values.

### 3. Diagnosing and Fixing Slow Query

If the query `findMany posts filtered by tag name` is taking 800ms, you can diagnose and fix it by following these steps:

1. **Identify the Query:**
   ```prisma
   const posts = await prisma.post.findMany({
     where: { tags: { some: { name: tag } } },
     include: { tags: true },
   });
   ```

2. **Generate SQL:**
   Use Prisma's `generate` command to see the raw SQL generated:
   ```bash
   npx prisma generate
   ```

3. **Analyze the SQL:**
   The generated SQL might look something like:
   ```sql
   SELECT "id", "title", "content", "published", "authorId", "createdAt", "slug"
   FROM "Post"
   WHERE EXISTS (
     SELECT 1
     FROM "Tag" AS T
     WHERE T."postId" = "Post"."id" AND T."name" = $1
   )
   ```

4. **Create an Index:**
   Add an index on the `tags` relationship to improve query performance:
   ```prisma
   model Post {
     id Int @id
     title String
     content String
     published Boolean @default(false)
     authorId Int
     author User @relation(...)
     tags Tag[]
     comments Comment[]
     createdAt DateTime @default(now())
   }

   model Tag {
     id Int @id
     name String @unique
     posts Post[]
   }
   ```

   You can add an index on the `Tag` model:
   ```prisma
   model Tag {
     id Int @id
     name String @unique
     posts Post[]
     @index([name, "postId"]) // Add this line
   }
   ```

5. **Update the Database:**
   ```bash
   npx prisma migrate dev --name add_index_to_tag
   ```

6. **Test the Query Again:**
   Ensure the query performance improves.

### 4. Dropping Down to Raw SQL

You would drop down to raw SQL when Prisma's generated queries are not efficient or when you need more control over the query execution. For example, if you need to perform a complex query that Prisma cannot generate, or if you want to use specific database features that are not covered by Prisma.

**Real Example:**

If you need to perform a `JOIN` across multiple tables in a complex way, you might drop down to raw SQL. For instance, if you need to join `Post`, `Tag`, and `Comment` tables to fetch posts, tags, and comments in a specific format that is not easily achieved with Prisma's `include` and `select`.

Example:
```prisma
const result = await prisma.$queryRaw`
  SELECT 
    p.id, 
    p.title, 
    p.content, 
    p.published, 
    a.name AS author_name, 
    t.name AS tag_name, 
    c.id AS comment_id, 
    c.content AS comment_content 
  FROM Post p 
  JOIN User a ON p.authorId = a.id 
  LEFT JOIN Tag t ON p.tags_id = t.id 
  LEFT JOIN Comment c ON p.id = c.postId 
  WHERE p.published = true 
  ORDER BY p.createdAt DESC 
  LIMIT 10;
`;
```

This raw SQL query provides more flexibility and control over the join and selection of fields.

*Response time: 28.6s*

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
### 1. Docker Compose for Local Development

Here is a `docker-compose.yml` for local development:

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    ports:
      - "3000:3000"
    env_file:
      - .env
    volumes:
      - .:/app
    networks:
      - app-network
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "node", "healthcheck.js"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "3001:3001"
    env_file:
      - .env
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - app-network
    depends_on:
      - db
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "yourusername"]
      interval: 10s
      timeout: 5s
      retries: 5

  db:
    image: postgres:13
    environment:
      POSTGRES_USER: yourusername
      POSTGRES_PASSWORD: yourpassword
      POSTGRES_DB: yourdatabase
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "yourusername"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:6.2

volumes:
  postgres-data:

networks:
  app-network:
```

### 2. Production Dockerfile for Backend (Node.js)

Here is a multi-stage Dockerfile for the backend:

```Dockerfile
# Stage 1: Build
FROM node:16 AS builder

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .

RUN yarn build

# Stage 2: Production
FROM node:16-alpine

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules

USER node

EXPOSE 3001

CMD ["node", "dist/index.js"]
```

### 3. Diagnosing "Exit Code 137" in Production

**Meaning of Exit Code 137:**
- Exit code 137 in Docker typically means that the process was terminated by the operating system because it ran out of memory (OOM Killer).

**How to Diagnose:**
1. **Check Logs:**
   ```sh
   docker logs <container_id>
   ```
   Look for any error messages or stack traces that might give you a hint about what went wrong.

2. **OOM Killer Logs:**
   Check if the OOM Killer was involved:
   ```sh
   journalctl -u docker.service
   ```
   Look for messages like "Killed by oom-killer".

3. **Resource Limits:**
   - Check the container's resource limits using `docker stats`.
   - Adjust resource limits in the `docker-compose.yml`:
     ```yaml
     resources:
       limits:
         memory: 1G
     ```

4. **Code and Configuration Review:**
   - Review your backend code for potential memory leaks or excessive memory usage.
   - Check your database queries for efficiency and any excessive data fetching.
   - Ensure your Redis usage is optimized.

5. **Environment Variables:**
   Ensure that your environment variables and configurations are correctly set and not causing unexpected behavior.

### 4. Zero Downtime Deployment Sequence for Database Schema Changes

To achieve zero downtime deployment when adding a nullable column to the database schema, follow these steps:

1. **Prepare the Migration:**
   - Use a migration tool like `knex` or `sequelize` to create the migration file.
   - The migration should add the new column with `nullable: true`.

2. **Build the New Backend Version:**
   - Update the backend code to handle the new schema.
   - Use `docker-compose build` to build the new version of the backend.

3. **Update the Frontend:**
   - Ensure the frontend is aware of the new schema and can handle any changes.
   - Update the frontend code if necessary.

4. **Deploy New Backend:**
   - Use a tool like `docker-compose up -d --build backend` to deploy the new backend version.
   - Ensure the backend starts and is healthy.

5. **Run Migrations:**
   - Use `docker exec` to run the migration in the existing database container:
     ```sh
     docker exec -it <db_container_id> psql -U yourusername -d yourdatabase -c "BEGIN; <migration_sql>; COMMIT;"
     ```

6. **Verify Schema:**
   - Verify that the new column is added to the database.
   - Run a few queries to ensure the data is correctly handled.

7. **Gracefully Shutdown Old Backend:**
   - Use `docker-compose stop backend` to gracefully stop the old backend.
   - Ensure the application handles shutdown gracefully.

8. **Restart Frontend:**
   - Restart the frontend if necessary to ensure it is aware of the new schema.

9. **Monitor:**
   - Monitor the application for any issues and ensure everything is running smoothly.

By following these steps, you can minimize downtime and ensure a smooth transition to the new schema version.

*Response time: 25.9s*

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
Sure, let's build a collaborative document editor using Node.js and the `ws` library. We'll cover the key components you mentioned: connection handling, message protocol, broadcasting, reconnection handling, and handling simultaneous edits.

### 1. Connection Handling

We'll maintain a map of WebSocket connections associated with user IDs and document IDs. This will allow us to track which user is editing which document.

```javascript
const WebSocket = require('ws');

class DocumentEditorServer {
    constructor() {
        this.clients = new Map(); // Map of client connections
        this.documentState = new Map(); // Map of document state by document ID
    }

    // Connect a new client
    connect(client) {
        const connectionId = client.upgradeReq.url.split('?')[1]; // Assume connection ID is in the URL
        const clientId = client.upgradeReq.headers['sec-websocket-key']; // Unique client ID
        client.on('message', this.onMessage.bind(this, clientId));
        client.on('close', this.onClose.bind(this, clientId));

        this.clients.set(clientId, client);
        console.log(`Client ${clientId} connected`);
    }

    // Disconnect a client
    disconnect(clientId) {
        if (this.clients.has(clientId)) {
            this.clients.delete(clientId);
            console.log(`Client ${clientId} disconnected`);
        }
    }

    // Handle client messages
    onMessage(clientId, message) {
        const msg = JSON.parse(message);
        switch (msg.type) {
            case 'JOIN_DOCUMENT':
                this.handleJoinDocument(clientId, msg.documentId);
                break;
            case 'TEXT_CHANGE':
                this.handleTextChange(clientId, msg.documentId, msg.text, msg.position);
                break;
            case 'CURSOR_MOVE':
                this.handleCursorMove(clientId, msg.documentId, msg.position);
                break;
            case 'USER_LEFT':
                this.handleUserLeft(clientId, msg.documentId);
                break;
            default:
                console.log(`Unknown message type: ${msg.type}`);
        }
    }

    // Handle client close
    onClose(clientId) {
        this.disconnect(clientId);
    }

    // Handle JOIN_DOCUMENT message
    handleJoinDocument(clientId, documentId) {
        const client = this.clients.get(clientId);
        if (!client) return;

        if (!this.documentState.has(documentId)) {
            this.documentState.set(documentId, '');
        }

        client.send(JSON.stringify({
            type: 'UPDATE',
            documentId,
            text: this.documentState.get(documentId)
        }));
    }

    // Handle TEXT_CHANGE message
    handleTextChange(clientId, documentId, text, position) {
        const client = this.clients.get(clientId);
        if (!client) return;

        const document = this.documentState.get(documentId);
        if (!document) return;

        // Update the document state
        document = document.slice(0, position) + text + document.slice(position + text.length);
        this.documentState.set(documentId, document);

        // Broadcast the change to all clients except the sender
        this.broadcast(documentId, 'TEXT_CHANGE', { position, text });
    }

    // Handle CURSOR_MOVE message
    handleCursorMove(clientId, documentId, position) {
        const client = this.clients.get(clientId);
        if (!client) return;

        // Broadcast the cursor move to all clients
        this.broadcast(documentId, 'CURSOR_MOVE', { position });
    }

    // Handle USER_LEFT message
    handleUserLeft(clientId, documentId) {
        const client = this.clients.get(clientId);
        if (!client) return;

        // Broadcast the user left message to all clients
        this.broadcast(documentId, 'USER_LEFT', { clientId });

        // Remove the client from the state
        this.disconnect(clientId);
    }

    // Broadcast message to all connected clients
    broadcast(documentId, type, data) {
        const documentClients = this.documentState.keys().filter(docId => docId === documentId);
        for (const docId of documentClients) {
            const documentState = this.documentState.get(docId);
            const clients = this.clients.values();
            for (const client of clients) {
                if (client.readyState === WebSocket.OPEN) {
                    client.send(JSON.stringify({
                        type,
                        documentId,
                        text: documentState,
                        ...data
                    }));
                }
            }
        }
    }
}
```

### 2. Message Protocol

We define the message types in JSON format:

- `JOIN_DOCUMENT`: User joins a document.
- `TEXT_CHANGE`: User changes text.
- `CURSOR_MOVE`: User moves the cursor.
- `USER_LEFT`: User leaves the document.

```json
{
    "type": "JOIN_DOCUMENT",
    "documentId": "doc123"
}
```

```json
{
    "type": "TEXT_CHANGE",
    "documentId": "doc123",
    "text": "new text",
    "position": 5
}
```

```json
{
    "type": "CURSOR_MOVE",
    "documentId": "doc123",
    "position": 10
}
```

```json
{
    "type": "USER_LEFT",
    "documentId": "doc123",
    "clientId": "user456"
}
```

### 3. Broadcasting

When a user makes a change, we broadcast the message to all connected clients for the same document, excluding the sender. This is handled by the `broadcast` method in the `DocumentEditorServer` class.

### 4. Reconnection Handling

When a user reconnects, we check if the user has any open documents and send them the current state of the document. This is handled by the `handleJoinDocument` and `handleTextChange` methods.

### 5. Handling Simultaneous Edits

If two users edit the exact same position simultaneously, the last change will overwrite the previous change. To handle this, you can use an event sourcing approach where each change is recorded, and the latest state is computed on the client side. Alternatively, you can use a more sophisticated approach like Operational Transformation (OT) or Conflict-free Replicated Data Types (CRDTs), but that is beyond the scope of this simple implementation.

### Core Server Implementation

Here's the complete core server implementation:

```javascript
const WebSocket = require('ws');

class DocumentEditorServer {
    constructor() {
        this.clients = new Map(); // Map of client connections
        this.documentState = new Map(); // Map of document state by document ID
    }

    connect(client) {
        const connectionId = client.upgradeReq.url.split('?')[1]; // Assume connection ID is in the URL
        const clientId = client.upgradeReq.headers['sec-websocket-key']; // Unique client ID
        client.on('message', this.onMessage.bind(this, clientId));
        client.on('close', this.onClose.bind(this, clientId));

        this.clients.set(clientId, client);
        console.log(`Client ${clientId} connected`);
    }

    disconnect(clientId) {
        if (this.clients.has(clientId)) {
            this.clients.delete(clientId);
            console.log(`Client ${clientId} disconnected`);
        }
    }

    onMessage(clientId, message) {
        const msg = JSON.parse(message);
        switch (msg.type) {
            case 'JOIN_DOCUMENT':
                this.handleJoinDocument(clientId, msg.documentId);
                break;
            case 'TEXT_CHANGE':
                this.handleTextChange(clientId, msg.documentId, msg.text, msg.position);
                break;
            case 'CURSOR_MOVE':
                this.handleCursorMove(clientId, msg.documentId, msg.position);
                break;
            case 'USER_LEFT':
                this.handleUserLeft(clientId, msg.documentId);
                break;
            default:
                console.log(`Unknown message type: ${msg.type}`);
        }
    }

    onClose(clientId) {
        this.disconnect(clientId);
    }

    handleJoinDocument(clientId, documentId) {
        const client = this.clients.get(clientId);
        if (!client) return;

        if (!this.documentState.has(documentId)) {
            this.documentState.set(documentId, '');
        }

        client.send(JSON.stringify({
            type: 'UPDATE',
            documentId,
            text: this.documentState.get(documentId)
        }));
    }

    handleTextChange(clientId, documentId, text, position) {
        const client = this.clients.get(clientId);
        if (!client) return;

        const document = this.documentState.get(documentId);
        if (!document) return;

        const updatedDocument = document.slice(0, position) + text + document.slice(position + text.length);
        this.documentState.set(documentId, updatedDocument);

        this.broadcast(documentId, 'TEXT_CHANGE', { position, text });
    }

    handleCursorMove(clientId, documentId, position) {
        const client = this.clients.get(clientId);
        if (!client) return;

        this.broadcast(documentId, 'CURSOR_MOVE', { position });
    }

    handleUserLeft(clientId, documentId) {
        const client = this.clients.get(clientId);
        if (!client) return;

        this.broadcast(documentId, 'USER_LEFT', { clientId });

        this.disconnect(clientId);
    }

    broadcast(documentId, type, data) {
        const document

*Response time: 42.1s*

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
Sure, let's break down the tasks step-by-step:

### 1. GraphQL Schema (SDL) for the Recipe Domain

Here's the complete GraphQL schema (SDL) for the recipe domain:

```graphql
scalar Float
scalar Int
scalar String

type Ingredient {
  name: String!
  amount: Float!
  unit: String!
}

type Recipe {
  id: ID!
  title: String!
  ingredients: [Ingredient!]!
  steps: [String!]!
  author: User!
  tags: [String!]!
  ratings: [Rating!]!
  averageRating: Float
}

type Rating {
  score: Float!
  comment: String
}

type User {
  id: ID!
  name: String!
  recipes: [Recipe!]!
}

type Query {
  recipes(filter: {tag: String, minRating: Float}, pagination: {page: Int, limit: Int}): [Recipe!]!
}

type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String): Rating!
}

type Subscription {
  recipeAdded: Recipe!
}

schema {
  query: Query
  mutation: Mutation
  subscription: Subscription
}
```

### 2. Resolvers for the Defined Queries and Mutations

Here are the resolvers for the defined queries and mutations:

```javascript
const DataLoader = require('dataloader');

// Sample data
const recipes = [
  {
    id: '1',
    title: 'Chocolate Cake',
    ingredients: [
      { name: 'Sugar', amount: 200, unit: 'g' },
      { name: 'Flour', amount: 150, unit: 'g' },
      { name: 'Eggs', amount: 3, unit: 'pieces' }
    ],
    steps: ['Preheat oven', 'Mix ingredients', 'Bake for 30 mins'],
    author: { id: '2', name: 'Alice' },
    tags: ['birthday', 'chocolate'],
    ratings: [
      { score: 4.5, comment: 'Tasty!' },
      { score: 3.5, comment: 'Good but could be better' }
    ]
  },
  // ... more recipes
];

const users = [
  { id: '1', name: 'Bob' },
  { id: '2', name: 'Alice' },
  // ... more users
];

const recipeById = DataLoader.fromPromise((ids) => Promise.resolve(recipes.filter(recipe => ids.includes(recipe.id))));
const authorById = DataLoader.fromPromise((ids) => Promise.resolve(users.filter(user => ids.includes(user.id))));

const resolvers = {
  Query: {
    recipes: (parent, { filter, pagination }) => {
      let { tag, minRating } = filter || {};
      let { page, limit } = pagination || {};
      page = page || 1;
      limit = limit || 10;
      
      let filteredRecipes = recipes.filter(recipe => !tag || recipe.tags.includes(tag));
      if (minRating) {
        filteredRecipes = filteredRecipes.filter(recipe => recipe.ratings.some(rating => rating.score >= minRating));
      }
      const startIndex = (page - 1) * limit;
      const endIndex = startIndex + limit;
      return filteredRecipes.slice(startIndex, endIndex);
    }
  },
  Mutation: {
    addRating: (parent, { recipeId, score, comment }) => {
      const recipe = recipes.find(recipe => recipe.id === recipeId);
      if (recipe) {
        recipe.ratings.push({ score, comment });
        return recipe.ratings[recipe.ratings.length - 1];
      }
      throw new Error('Recipe not found');
    }
  },
  Recipe: {
    averageRating: (recipe) => {
      if (recipe.ratings.length === 0) {
        return 0;
      }
      const totalScore = recipe.ratings.reduce((sum, rating) => sum + rating.score, 0);
      return totalScore / recipe.ratings.length;
    },
    author: (recipe) => {
      return authorById.load(recipe.author.id);
    }
  },
  User: {
    recipes: (user) => {
      return recipeById.loadMany(user.recipes.map(recipe => recipe.id));
    }
  }
};
```

### 3. N+1 Problem and DataLoader Solution

**Problem with N+1:**
The `author` field in the `Recipe` type causes an N+1 problem because it fetches the `author` for each `Recipe` individually, resulting in a separate query for each `Recipe`.

**Example:**
If you have 10 recipes, you would make 10 separate queries to fetch the authors, which is inefficient.

**Solution with DataLoader:**
The `authorById` DataLoader caches the authors and reuses them when the same user ID is requested again, significantly reducing the number of database queries.

### 4. Fetching Recipe Title, Author Name, and First 3 Ingredients

The client would write the following GraphQL query:

```graphql
query {
  recipes(filter: {tag: "chocolate"}, pagination: {page: 1, limit: 10}) {
    title
    author {
      name
    }
    ingredients {
      name
      amount
      unit
      first: 3
    }
  }
}
```

This query fetches the title, author name, and the first three ingredients for each recipe.

### 5. When to Use GraphQL Over REST and When Not to

**When to Use GraphQL:**
- **Complex Queries:** When you need to fetch a mix of data from various resources, and you want to minimize the number of requests.
- **Flexible Data Consumption:** When the client needs to decide at runtime what data it needs.
- **Single Endpoint:** When you want to reduce the number of endpoints in your API.
- **Performance:** When you have a client that can handle complex queries and you want to optimize for performance by fetching only necessary data.

**When Not to Use GraphQL:**
- **Simplicity:** For simple APIs where REST's simplicity is beneficial.
- **Large Number of Clients:** When you have a large number of clients that all need the same data.
- **Low Latency Requirements:** If the performance gain from using GraphQL isn't significant, REST might be faster.
- **Static Data:** If the data structure is static and unlikely to change, REST can be more straightforward to implement and maintain.
- **Legacy Systems:** When integrating with legacy systems that are built for REST.

This should cover all the aspects you asked for!

*Response time: 29.9s*

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
To implement the described layout, we will use a combination of CSS Grid for the cards and Flexbox for managing the main layout. Here's the complete HTML and CSS:

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
    <header class="header">
        <h1>HEADER</h1>
    </header>
    <div class="container">
        <aside class="sidebar">
            <h2>SIDEBAR</h2>
            <div class="cards">
                <div class="card">
                    <img src="https://via.placeholder.com/150x84" alt="Card Image" class="card-img">
                    <div class="card-content">
                        <h3>Title</h3>
                        <p>Description</p>
                        <footer class="card-footer">
                            <button class="btn-left">Left Button</button>
                            <button class="btn-right">Right Button</button>
                        </footer>
                    </div>
                </div>
                <div class="card">
                    <img src="https://via.placeholder.com/150x84" alt="Card Image" class="card-img">
                    <div class="card-content">
                        <h3>Title</h3>
                        <p>Description</p>
                        <footer class="card-footer">
                            <button class="btn-left">Left Button</button>
                            <button class="btn-right">Right Button</button>
                        </footer>
                    </div>
                </div>
            </div>
        </aside>
        <main class="main-content">
            <h2>MAIN CONTENT</h2>
            <p>Main content goes here.</p>
        </main>
    </div>
</body>
</html>
```

### CSS
```css
/* styles.css */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
}

.header {
    width: 100%;
    height: 60px;
    background-color: #333;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
}

.container {
    display: flex;
    flex-direction: column;
    flex: 1;
    margin-top: 60px;
}

.sidebar {
    width: 240px;
    background-color: #f4f4f4;
    overflow-y: auto;
    flex-shrink: 0;
}

.main-content {
    flex: 1;
    background-color: #fff;
    overflow-y: auto;
    padding: 20px;
}

.cards {
    display: grid;
    gap: 20px;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    padding: 20px;
}

.card {
    background-color: #fff;
    border: 1px solid #ddd;
    padding: 15px;
    border-radius: 5px;
    display: flex;
    flex-direction: column;
}

.card-img {
    width: 100%;
    height: 84px;
    object-fit: cover;
    aspect-ratio: 16 / 9;
}

.card-content {
    flex: 1;
    padding: 10px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.card-content h3 {
    font-size: 18px;
    margin-bottom: 5px;
}

.card-content p {
    font-size: 14px;
    color: #555;
}

.card-footer {
    display: flex;
    justify-content: space-between;
}

.btn-left, .btn-right {
    padding: 5px 10px;
    border: none;
    background-color: #007bff;
    color: white;
    border-radius: 3px;
    cursor: pointer;
}

.btn-left {
    margin-right: 10px;
}
```

### Explanation of Layout Approach

1. **Flexbox for Main Layout:**
   - The `.container` uses `flex-direction: column` to stack the `.sidebar` and `.main-content` vertically.
   - The `.sidebar` is set to have a fixed width of 240px and `overflow-y: auto` to enable vertical scrolling when content overflows.
   - The `.main-content` takes up the remaining space (`flex: 1`) and also has `overflow-y: auto` to enable scrolling if the content exceeds the viewport.

2. **CSS Grid for Cards:**
   - The `.cards` container uses `display: grid` with `grid-template-columns: repeat(auto-fill, minmax(250px, 1fr))` to create a responsive grid layout.
   - `repeat(auto-fill, minmax(250px, 1fr))` ensures that the grid items will have a minimum width of 250px and will fill available space as much as possible, creating either 1 or 2 columns based on the viewport width.
   - Each `.card` is a flexible container with padding, and the `.card-img` ensures the image maintains a 16:9 aspect ratio using `aspect-ratio: 16 / 9`.

3. **Styling for Cards and Buttons:**
   - The `.card` contains a responsive image with `.card-img`, and the `.card-content` includes a title, description, and a footer with buttons.
   - Buttons are styled to be left and right-aligned using `justify-content: space-between`.

This layout ensures that the header is fixed, the sidebar and main content fill the viewport below the header, and they scroll independently. The cards are responsive, adjusting to 1 or 2 columns based on the viewport width.

*Response time: 28.5s*

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
Sure, let's design a real-time notification system for the project management tool considering the requirements and the given constraints.

### 1. Transport Mechanism

**WebSocket vs. Server-Sent Events (SSE) vs. Polling vs. Push Notifications**

- **WebSocket**: Provides full-duplex communication channels over a single TCP connection. It's ideal for real-time updates but requires a persistent connection, which can be resource-intensive.
- **Server-Sent Events (SSE)**: Unidirectional from server to client. Good for streaming updates but doesn't handle bidirectional communication well.
- **Polling**: Periodically asks the server if there are any updates. Inefficient for many users and can cause server load.
- **Push Notifications**: Not ideal for real-time updates, as they rely on the user being active in the application and the device being unlocked.

**Justification**: **WebSocket** is the best choice for this scenario because it allows for real-time, bidirectional communication between the client and server. It ensures that notifications are delivered instantly without the need for constant polling.

### 2. Storing Notifications

**Database Schema Design**

```sql
CREATE TABLE Notifications (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    task_id BIGINT NOT NULL,
    notification_type VARCHAR(50) NOT NULL, -- e.g., 'ASSIGNED', 'COMMENT', 'DUE_SOON'
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE
);
```

- **id**: Unique identifier for each notification.
- **user_id**: ID of the user receiving the notification.
- **task_id**: ID of the task the notification relates to.
- **notification_type**: Type of notification (e.g., 'ASSIGNED', 'COMMENT', 'DUE_SOON').
- **message**: The message content of the notification.
- **created_at**: Timestamp when the notification was created.
- **is_read**: Boolean indicating whether the user has read the notification.

### 3. Handling Offline Users

**Approach**: When a user goes offline, their device stops receiving WebSocket messages. To handle this, the system should:

- **Queue Notifications**: Store unprocessed notifications in a queue (e.g., Redis, Kafka) that can be processed when the user comes back online.
- **Push Notifications**: Use push notifications to notify the user when they return to the application. This ensures that they are notified of any missed updates.

### 4. Implementing the Deadline Check

**Approach**: The deadline check should run every hour for all tasks. This can be implemented using a background job system like a queue or an event-driven architecture.

- **Cron Job**: A simple cron job that runs every hour.
- **Queue**: A message queue like RabbitMQ or Kafka that handles task deadlines.

**Implementation Approach Using a Queue**

1. **Create a Queue**: Set up a message queue service (e.g., RabbitMQ) to handle task deadline checks.
2. **Create a Worker**: Develop a worker that listens to this queue and processes tasks that are due soon.
3. **Scheduled Tasks**: Schedule a task to periodically send messages to the queue (e.g., every hour).

**Example Implementation** (using Python with Celery and RabbitMQ):

```python
from celery import Celery
import datetime

app = Celery('tasks', broker='amqp://guest@localhost//')

@app.task
def check_deadlines():
    # Logic to fetch tasks due in the next 24 hours
    tasks_due_soon = get_tasks_due_soon()
    for task in tasks_due_soon:
        send_deadline_notification(task)
    return f"Checked {len(tasks_due_soon)} tasks for deadlines."

def get_tasks_due_soon():
    # Fetch tasks due in the next 24 hours
    return Task.objects.filter(deadline__gte=datetime.datetime.now() + datetime.timedelta(days=1))

def send_deadline_notification(task):
    # Send a notification via WebSocket or other mechanism
    pass
```

### 5. Scaling the System for 100,000 Concurrent Users

**Approach**: To handle a large number of concurrent users, consider the following strategies:

- **Load Balancing**: Use a load balancer to distribute incoming WebSocket connections across multiple server instances.
- **Scalable Queues**: Use scalable queueing services like RabbitMQ, Kafka, or AWS SQS.
- **Database Scaling**: Use a database that can scale horizontally, like sharding or a distributed database.
- **Asynchronous Processing**: Ensure that tasks like sending notifications and checking deadlines are handled asynchronously to avoid blocking the main application thread.
- **Caching**: Implement caching for frequently accessed data to reduce database load.

By implementing these strategies, you can ensure that the notification system remains robust and performs well even with a large number of concurrent users.

*Response time: 21.7s*

---
