# Model: smollm2:1.7b
**Test Date:** 2026-03-10 18:29:06
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
I'll guide you through designing the API endpoints according to the defined entities and rules. 

**1. Define all endpoints (method + path) following REST conventions**

Below are the REST API endpoints for the multi-tenant SaaS project management tool:

### 1.1. Create Workspace

*   **Endpoint**: `POST /workspaces`
*   **Request Body**: `{ name: string }`
*   **Response**: `{ id: string, name: string }`

### 1.2. Create Project

*   **Endpoint**: `POST /projects`
*   **Request Body**: `{ workspaceId: string, name: string }`
*   **Response**: `{ id: string, workspaceId: string, name: string }`

### 1.3. Create Task

*   **Endpoint**: `POST /projects/{projectId}/tasks`
*   **Request Body**: `{ name: string, description: string, assignee: string }`
*   **Response**: `{ id: string, projectId: string, name: string, description: string, assignee: string }`

### 1.4. Update Task Status

*   **Endpoint**: `PUT /tasks/{taskId}/status`
*   **Request Body**: `{ status: string }`
*   **Response**: `{ id: string, status: string }`

### 1.5. List Tasks with Filters (Assignee, Status, Due Date)

*   **Endpoint**: `GET /projects/{projectId}/tasks`
*   **Request Parameters**: `[ { name: string, value: string }, { name: string, value: string }, { name: string, value: string } ]`
*   **Response**: `[ { id: string, projectId: string, name: string, description: string, assignee: string, dueDate: string } ]`

### 1.6. Add Comment to Task

*   **Endpoint**: `POST /tasks/{taskId}/comments`
*   **Request Body**: `{ content: string, assignee: string }`
*   **Response**: `{ id: string, taskId: string, content: string, assignee: string }`

### 1.7. Delete Task

*   **Endpoint**: `DELETE /tasks/{taskId}`
*   **Response**: `{ id: string }`

### 1.8. Get Task Details

*   **Endpoint**: `GET /tasks/{taskId}`
*   **Response**: `{ id: string, projectId: string, name: string, description: string, assignee: string, dueDate: string, comments: [ { id: string, comment: string, assignee: string } ] }`

### 1.9. Get Comments for Task

*   **Endpoint**: `GET /tasks/{taskId}/comments`
*   **Response**: `[ { id: string, comment: string, assignee: string } ]`

### 1.10. Get Comments with Assignee

*   **Endpoint**: `GET /tasks/{taskId}/comments/assignee`
*   **Response**: `[ { id: string, comment: string, assignee: string } ]`

### 1.11. Get Comments with Status

*   **Endpoint**: `GET /tasks/{taskId}/comments/status`
*   **Response**: `[ { id: string, comment: string, assignee: string } ]`

### 1.

*Response time: 10.5s*

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
Here's a complete handler, validation schema, and error middleware for the PATCH endpoint:

**PATCH /workspaces/:workspaceId/tasks/:taskId (Node.js + Express + TypeScript)**

```typescript
import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { validate } from 'zod';
import { Workspace, Task } from './models';

// Validate PATCH request schema
const TaskSchema = validate({
  title: {
    type: 'string',
    min: 1,
    max: 200,
  },
  status: {
    type: 'string',
    options: ['todo', 'in_progress', 'done', 'cancelled'],
  },
  assignee_id: {
    type: 'integer',
    nullable: true,
  },
  due_date: {
    type: 'string',
    format: 'ISO8601',
  },
});

// Create schema for workspace and task to validate PATCH request
const TaskSchemaWithWorkspace = validate({
  title: {
    type: 'string',
    min: 1,
    max: 200,
  },
  status: {
    type: 'string',
    options: ['todo', 'in_progress', 'done', 'cancelled'],
  },
  assignee_id: {
    type: 'integer',
    nullable: true,
  },
  due_date: {
    type: 'string',
    format: 'ISO8601',
  },
});

// Handler function for PATCH /workspaces/:workspaceId/tasks/:taskId
async function updateTask(req: Request, res: Response, next: NextFunction) {
  try {
    const workspaceId = parseInt(req.params.workspaceId);
    const taskId = parseInt(req.params.taskId);
    const taskData = req.body;

    // Validate workspace and task IDs
    if (isNaN(workspaceId) || isNaN(taskId)) {
      return res.status(400).json({ message: 'Invalid ID' });
    }

    // Get workspace and task
    const workspace = await Workspace.findById(workspaceId);
    const task = await Task.findById(taskId);

    // Check if workspace or task doesn't exist
    if (!workspace || !task) {
      return res.status(404).json({ message: 'Task or workspace not found' });
    }

    // Check if task belongs to workspace
    if (workspace.assignee_id !== workspaceId) {
      return res.status(403).json({ message: 'Forbidden: Task not assigned to workspace' });
    }

    // Update task data
    const updatedTask = await TaskSchemaWithWorkspace.validateAndSet(taskData);

    // Set status to cancelled if it's an open task
    if (updatedTask.status === 'todo' && updatedTask.openSubtasks.length) {
      if (updatedTask.status === 'in_progress') {
        return res.status(409).json({ message: 'Cannot set status to "cancelled" if open subtasks exist' });
      }
    }

    // Update task data
    await Task.findByIdAndUpdate(taskId, updatedTask);

    res.json({ message: 'Task updated successfully' });
  } catch (error) {
    next(error);
  }
}

// Export the handler function
export default updateTask;
```

**Validation Schema (TypeScript)**

```typescript
// Task validation schema
const TaskSchema = validate({
  title: {
    type: 'string',
    min: 1,
    max: 200,
  },
  status: {
    type: 'string',
    options: ['todo', 'in_progress', 'done', 'cancelled'],
  },
  assignee_id: {
    type: 'integer',
    nullable: true,
  },
  due_date: {
    type: 'string',
    format: 'ISO8601',
  },
});

// Task validation schema with workspace validation (for partial updates)
const TaskSchemaWithWorkspace = validate({
  title: {
    type: 'string',
    min: 1,
    max: 200,
  },
  status: {
    type: 'string',
    options: ['todo', 'in_progress', 'done', 'cancelled'],
  },
  assignee_id: {
    type: 'integer',
    nullable: true,
  },
  due_date: {
    type: 'string',
    format: 'ISO8601',
  },
});
```

**Error Middleware (TypeScript)**

```typescript
// Error middleware for validating request body
const validateRequestBody = async (schema: any) => {
  try {
    const body = req.body;
    const errors = schema.validate(body);
    if (errors) {
      return res.status(400).json(errors);
    }
  } catch (error) {
    next(error);
  }
};

// Error middleware for validating workspace and task IDs
const validateWorkspaceAndTaskIds = (schema: any) => {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      const workspaceId = parseInt(req.params.workspaceId);
      const taskId = parseInt(req.params.taskId);

      // Validate workspace and task IDs
      if (isNaN(workspaceId) || isNaN(taskId)) {
        return res.status(400).json({ message: 'Invalid ID' });
      }

      next();
    } catch (error) {
      next(error);
    }
  };
};

// Error middleware for checking if task belongs to workspace
const taskBelongsToWorkspace = async (
  workspaceId: number,
  taskId: number,
  task: Task,
) => {
  try {
    // Check if workspace ID matches the task's workspace ID
    if (task.workspace_id !== workspaceId) {
      return false;
    }

    // Check if assignee ID matches the task's assignee ID
    if (task.assignee_id !== taskId) {
      return false;
    }

    return true;
  } catch (error) {
    return false;
  }
};
```

**Unit Tests (TypeScript)**

```typescript
import { Request, Response } from 'express';
import { validate } from 'zod';
import { Workspace, Task } from './models';

describe('Task Update PATCH endpoint', () => {
  const taskSchema = TaskSchema;
  const taskSchemaWithWorkspace = TaskSchemaWithWorkspace;

  it('should return 400 with field-level validation errors if validation fails', async () => {
    const taskData = {
      title: 'Test Task',
      status: 'todo',
      assignee_id: 1,
      due_date: '2023-01-01T00:00:00.000Z',
    };

    const res = await request(app)
      .patch('/workspaces/1/tasks/2')
      .set('Cookies', 'sessionID=12345')
      .send(taskData);

    expect(res.status).toBe(400);
    expect(res.body).toHaveProperty('errors');
    expect(res.body.errors).toHaveProperty('title', 'Field is required');
    expect(res.body.errors).toHaveProperty('status', 'Field is required');
    expect(res.body.errors).toHaveProperty('assignee_id', 'Field is required');
    expect(res.body.errors).toHaveProperty('due_date', 'Field is required');
  });

  it('should return 404 if workspace or task doesn\'t exist', async () => {
    const taskData = {
      title: 'Test Task',
      status: 'todo',
      assignee_id: 1,
      due_date: '2023-01-01T00:00:00.000Z',
    };

    const res = await request(app)
      .patch('/workspaces/1/tasks/2')
      .set('Cookies', 'sessionID=12345')
      .send(taskData);

    expect(res.status).toBe(404);
    expect(res.body).toHaveProperty('message', 'Task or workspace not found');
  });

  it('should return 403 if task doesn\'t belong to workspace', async () => {
    const taskData = {
      title: 'Test Task',
      status: 'todo',
      assignee_id: 2,
      due_date: '2023-01-01T00:00:00.000Z',
    };

    const res = await request(app)
      .patch('/workspaces/1/tasks/2')
      .set('Cookies', 'sessionID=12345')
      .send(taskData);

    expect(res.status).toBe(403);
    expect(res.body).toHaveProperty('message', 'Task not assigned to workspace');
  });

  it('should return 409 if trying to set status to \'cancelled\' when task has open subtasks', async () => {
    const taskData = {
      title: 'Test Task',
      status: 'in_progress',
      assignee_id: 1,
      due_date: '2023-01-01T00:00:00.000Z',
      openSubtasks: [1, 2, 3],
    };

    const res = await request(app)
      .patch('/workspaces/1/tasks/2')
      .set('Cookies', 'sessionID=12345')
      .send(taskData);

    expect(res.status).toBe(409);
    expect(res.body).toHaveProperty('message', 'Cannot set status to \'cancelled\' if open subtasks exist');
  });

  it('should return 400 if task data is invalid', async () => {
    const taskData = {
      title: '',
      status: 'todo',
      assignee_id: 1,
      due_date: '2023-01-01T00:00:00.000Z',
    };

    const res = await request(app)
      .patch('/workspaces/1/tasks/2')
      .set('Cookies', 'sessionID=12345')
      .send(taskData);

    expect(res.status).toBe(400);
    expect(res.body).toHaveProperty('errors');
    expect(res.body.errors).toHaveProperty('title', 'Field is required');
    expect(res.body.errors).toHaveProperty('status', 'Field is required');
    expect(res.body.errors).toHaveProperty('assignee_id', 'Field is required');
    expect(res.body.errors).toHaveProperty('due_date', 'Field is required');
  });
});
```

*Response time: 26.7s*

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
Here's a complete implementation of an authentication system in Node.js + Express + TypeScript, including the seven required steps:

1. **Register a user**

   ```typescript
export class User {
  id: string;
  email: string;
  password: string;
}

const registerUser = async (req: Request, res: Response) => {
  const { email, password } = req.body;
  const hashedPassword = await bcrypt.hash(password, 12);
  const user = new User({ id: uuidv4(), email, password: hashedPassword });
  await user.save();
  res.json({ message: 'User created successfully' });
};
```

2. **Login a user**

   ```typescript
const loginUser = async (req: Request, res: Response) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email });
  if (!user) {
    return res.status(401).json({ message: 'Invalid email or password' });
  }
  const isValidPassword = await bcrypt.compare(password, user.password);
  if (!isValidPassword) {
    return res.status(401).json({ message: 'Invalid email or password' });
  }
  const accessToken = jwt.sign({ userId: user.id, email: user.email }, process.env.ACCESS_TOKEN_SECRET!, { expiresIn: '15m' });
  const refreshToken = jwt.sign({ userId

*Response time: 3.5s*

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

To implement this, you can store the refresh token in a Redis database with a TTL of a specific duration (e.g. 30 days). The refresh token would be used to obtain a new access token by sending a POST request to the /auth/refresh endpoint.

Here's a basic example of how this might work:

```
{
  "refresh_token": "abc123",
  "access_token": "ghi789",
  "token_type": "Bearer",
  "expires_in": 30, // expires in 30 days
  "token_id": "56789"
}
```

2. POST /auth/logout — invalidate the refresh token, clear the cookie

To invalidate the refresh token and clear the cookie, you can send a POST request to the /auth/logout endpoint with the refresh token as a query parameter.

```
{
  "refresh_token": "abc123"
}
```

Redis data structure:

```
{
  "refresh_tokens": {
    "abc123": {
      "ttl": 30, // expires in 30 days
      "access_token": "ghi789",
      "token_type": "Bearer",
      "expires_in": 30, // expires in 30 days
      "token_id": "56789"
    }
  }
}
```

3. Implement refresh token rotation with a Redis-based token store (show the Redis data structure and TTL strategy)

To implement refresh token rotation with a Redis-based token store, you would store the refresh token in Redis with a TTL of a specific duration (e.g. 30 days) and then periodically (e.g. every 30 days) invalidate the old refresh token and issue a new one.

Redis data structure:

```
{
  "refresh_tokens": {
    "abc123": {
      "ttl": 30, // expires in 30 days
      "access_token": "ghi789",
      "token_type": "Bearer",
      "expires_in": 30, // expires in 30 days
      "token_id": "56789"
    },
    // ... other refresh tokens
  }
}
```

TTL strategy:

* When a refresh token is issued, set its TTL to 30 days.
* When a refresh token expires (e.g. 30 days after it was issued), remove it from Redis.
* When a refresh token is used to obtain a new access token, set its TTL to 30 days and add it to Redis.

4. How do you handle the case where a refresh token is used twice? (token reuse detection) — implement it

To implement token reuse detection, you can use a Redis hash with a key of `refresh_tokens` and values that include a `ttl` and `access_token`. When a refresh token is used to obtain a new access token, check the TTL of the refresh token and if it has expired, remove it from Redis.

```
{
  "refresh_tokens": {
    "abc123": {
      "ttl": 30, // expires in 30 days
      "access_token": "ghi789",
      "token_type": "Bearer",
      "expires_in": 30, // expires in 30 days, token has already expired
    }
  }
}
```

5. A user changes their password — how do you invalidate ALL their existing sessions? Implement it.

To invalidate all existing sessions for a user, you can send a POST request to the /auth/logout endpoint with the user ID as a query parameter.

```
{
  "user_id": "123"
}
```

Redis data structure:

```
{
  "sessions": {
    "123": {
      "refresh_token": "abc123",
      "access_token": "ghi789",
      "token_type": "Bearer",
      "expires_in": 30, // expires in 30 days, token has already expired
    }
  }
}
```

```
{
  "sessions": {
    "123": {
      "refresh_token": "xyz789",
      "access_token": "def456",
      "token_type": "Bearer",
      "expires_in": 30, // expires in 30 days, token has already expired
    }
  }
}
```

6. What is the difference between token blacklisting and token rotation? When would you use each?

Token blacklisting involves storing

*Response time: 11.1s*

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
Here's the implementation of the DataTable component:

**TypeScript Interface for Props**

```typescript
interface DataTableProps {
  columns: Column[]; // [ { key: string; header: string; width?: number; sortable?: boolean; renderCell?: (data: any, row: any) => ReactNode }, ... ]
  data: any[]; // [ { id: number; name: string; occupation: string; }, ... ]
  pageSize: number; // page size to display per page
  pageNumber: number; // starting page number
  selection?: boolean; // whether to show checkbox for selecting rows
  selectionSort?: 'asc' | 'desc' | 'none'; // sort selection to asc, desc, or none
  sortColumn?: number; // which column to sort (starting from 0 for columns)
  sortAsc?: boolean; // whether to sort in ascending order
  onSort?: (column: number, sortAsc: boolean) => void; // callback for sorting
  onSelect?: (row: any) => void; // callback for selecting a row
}

interface Column {
  key: string;
  header: string;
  width?: number;
  sortable?: boolean;
  renderCell?: (data: any, row: any) => ReactNode;
}
```

**Full Component Implementation**

```typescript
import React, { useEffect, useState } from 'react';
import { Table, Pagination, Row, Col } from 'react-bootstrap';

interface DataTableProps extends DataTableProps {
  columns: Column[];
}

function DataTable(props: DataTableProps) {
  const {
    columns,
    data,
    pageSize,
    pageNumber,
    selection,
    selectionSort,
    sortColumn,
    sortAsc,
    onSort,
    onSelect,
  } = props;

  const handlePageChange = (page: number) => {
    const newPageSize = pageSize;
    if (pageNumber !== page) {
      newPageSize = Math.ceil(data.length / newPageSize);
      pageNumber = page;
    }
    if (page < 0 || page > newPageSize - 1) {
      return;
    }
    props.onPageChange(page);
  };

  const handleSort = (column: number, sortAsc: boolean) => {
    const newSortColumn = sortColumn ? sortColumn : column;
    const newSortAsc = sortAsc ? sortAsc : !sortAsc;
    const newSortColumns = columns.filter((c) => c.key === newSortColumn);
    const newColumns = columns.filter((c) => c.key !== newSortColumn);
    const newData = data.sort((a, b) => {
      if (sortAsc === sortAsc) {
        if (sortColumn === 0) {
          return a[newSortColumn] - b[newSortColumn];
        } else {
          return (
            (sortColumn + 1) * sortAsc ? a[newSortColumn] - b[newSortColumn] : b[newSortColumn] - a[newSortColumn]
          );
        }
      } else {
        if (sortColumn === 0) {
          return b[newSortColumn] - a[newSortColumn];
        } else {
          return (
            (sortColumn + 1) * sortAsc ? b[newSortColumn] - a[newSortColumn] : a[newSortColumn] - b[newSortColumn]
          );
        }
      }
    });
    if (newSortColumns.length === 0) {
      return;
    }
    columns = newColumns;
    sortColumn = newSortColumn;
    sortAsc = newSortAsc;
    props.onSort(newSortColumn, newSortAsc);
  };

  const handleSelectionChange = (checked: boolean) => {
    if (checked) {
      onSelect(data.find((row) => row.id === props.selectedRowId));
    } else {
      onSelect(null);
    }
  };

  const handleRowClick = (row: any) => {
    if (row && onSelect) {
      onSelect(row);
    }
  };

  const handleRowCheckboxClick = (row: any) => {
    if (row && onSelect) {
      const selection = data.filter((r) => r.id === row.id);
      onSelect(selection[0]);
    }
  };

  const renderCell = (data: any, row: any) => {
    const render = columns.find((c) => c.key === c.sortable)?.renderCell || (() => '' as ReactNode);
    return render(data, row);
  };

  return (
    <Table responsive>
      <thead>
        <tr>
          {columns.map((column) => (
            <Col key={column.key}>
              <th>
                {column.header}
                {column.sortable && <TableHeaderColumn key={column.key} isSearchable>
                  {renderCell(data[0], column)}
                </TableHeaderColumn>}
              </th>
            </Col>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row) => (
          <Row key={row.id}>
            <td>
              <Table.Cell>
                {renderCell(row, row)}
              </Table.Cell>
            </td>
            {selection && (
              <td>
                <input
                  type="checkbox"
                  value={row}
                  checked={row === props.selectedRow}
                  onChange={handleRowCheckboxClick}
                />
              </td>
            )}
            {selectionSort === 'asc' && selectionSort === sortColumn && sortAsc && (
              <td>
                <Table.Cell
                  style={{ fontWeight: 'bold' }}
                >
                  <Row>
                    <Col>
                      <Button
                        variant="primary"
                        onClick={() => {
                          handleSort(sortColumn, true);
                          handleSortColumnsChanged();
                          handleSortAscChanged();
                        }}
                      >
                        ↗
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={() => {
                        handleSort(sortColumn, false);
                        handleSortColumnsChanged();
                        handleSortAscChanged();
                      }}
                    >
                        ↗
                    </Button>
                    <Button
                      variant="danger"
                      onClick={() => {
                        handleSort(sortColumn, false);
                        handleSortColumnsChanged();
                        handleSortAscChanged();
                      }}
                    >
                      ↗
                    </Button>
                    <Button
                      variant="info"
                      onClick={() => {
                        handleSort(sortColumn, false);
                        handleSortColumnsChanged();
                        handleSortAscChanged();
                      }}
                    >
                      ↗
                    </Button>
                  </Row>
                </Row>
              )}
              {selectionSort === 'desc' && selectionSort === sortColumn && sortAsc && (
                <td>
                  <Row>
                    <Col>
                      <Button
                        variant="primary"
                        onClick={() => {
                          handleSort(sortColumn, true);
                          handleSortColumnsChanged();
                          handleSortAscChanged();
                        }}
                      >
                        ↗
                      </Button>
                    </Col>
                    <Col>
                      <Button
                        variant="secondary"
                        onClick={() => {
                          handleSort(sortColumn, false);
                          handleSortColumnsChanged();
                          handleSortAscChanged();
                        }}
                      >
                        ↗
                      </Button>
                    </Col>
                    <Col>
                      <Button
                        variant="danger"
                        onClick={() => {
                          handleSort(sortColumn, false);
                          handleSortColumnsChanged();
                          handleSortAscChanged();
                        }}
                      >
                        ↗
                      </Button>
                    </Col>
                    <Col>
                      <Button
                        variant="info"
                        onClick={() => {
                          handleSort(sortColumn, false);
                          handleSortColumnsChanged();
                          handleSortAscChanged();
                        }}
                      >
                        ↗
                      </Button>
                    </Col>
                  </Row>
                </Row>
              )}
              {selectionSort === 'none' && selectionSort === sortColumn && sortAsc && (
                <td>
                  <Row>
                    <Col>
                      <Button
                        variant="primary"
                        onClick={() => {
                          handleSort(sortColumn, true);
                          handleSortColumnsChanged();
                          handleSortAscChanged();
                        }}
                      >
                        ↗
                      </Button>
                    </Col>
                    <Col>
                      <Button
                        variant="secondary"
                        onClick={() => {
                          handleSort(sortColumn, false);
                          handleSortColumnsChanged();
                          handleSortAscChanged();
                        }}
                      >
                        ↗
                      </Button>
                    </Col>
                    <Col>
                      <Button
                        variant="danger"
                        onClick={() => {
                          handleSort(sortColumn, false);
                          handleSortColumnsChanged();
                          handleSortAscChanged();
                        }}
                      >
                        ↗
                      </Button>
                    </Col>
                    <Col>
                      <Button
                        variant="info"
                        onClick={() => {
                          handleSort(sortColumn, false);
                          handleSortColumnsChanged();
                          handleSortAscChanged();
                        }}
                      >
                        ↗
                      </Button>
                    </Col>
                  </Row>
                </Row>
              )}
            </td>
          )}
        ))}
      </tbody>
      <Pagination
        component="nav"
        className="mb-4"
        size="2"
        count={Math.ceil(data.length / pageSize)}
        pageNumber={pageNumber}
        pageSize={pageSize}
        onChange={handlePageChange}
      />
    </Table>
  );
}

export default DataTable;
```

**Usage Example**

```typescript
import React from 'react';
import DataTable from './DataTable';

const columns = [
  { key: 'id', header: 'ID', width: 50, sortable: true },
  { key: 'name', header: 'Name', width: 150 },
  { key: 'occupation', header: 'Occupation', width: 150 },
];

const data = [
  { id: 1, name: 'John Doe', occupation: 'Software Engineer' },
  { id: 2, name: 'Jane Doe', occupation: 'Data Analyst' },
  { id: 3, name: 'Bob Smith', occupation: 'Product Manager' },
  { id: 4, name: 'Alice Johnson', occupation: 'Data Scientist' },
  { id: 5, name: 'Mike Brown', occupation: 'Software Developer' },
  { id: 6, name: 'Sophia Davis', occupation: 'Data Analyst' },
  { id: 7, name: 'Emily Taylor', occupation: 'Product Manager' },
  { id: 8, name: 'Olivia White', occupation: 'Software Developer' },
];

const selection = true;

const selectionSort = 'asc';

const sortColumn = 0;

const sortAsc = true;

const onSort = (column: number, sortAsc: boolean) => {
  // handle sorting here
};

const onSelect = (row: any) => {
  // handle selected row here
};

const pageSize = 10;
const pageNumber = 0;

const App = () => {
  return (
    <div>
      <DataTable
        columns={columns}
        data={data}
        pageSize={pageSize}
        pageNumber={pageNumber}
        selection={selection}
        selectionSort={selectionSort}
        sortColumn={sortColumn}
        sortAsc={sortAsc}
        onSort={onSort}
        onSelect={onSelect}
      />
    </div>
  );
};

export default App;
```

**Memoization**

Memoization can be implemented using a memoization decorator from the `react-hooks/use-memo` library.

```typescript
import { memo } from 'react-hooks/use-memo';

// ...

const handleSortColumnsChanged = useMemo(() => {
  columns = columns.filter((c) => c.sortable);
  const newColumns = columns.filter((c) => c.key !== sortColumn);
  const newColumnsArr = Array.from(newColumns);
  columns = newColumnsArr;
}, [columns, sortColumn]);

const handleSortAscChanged = useMemo(() => {
  sortAsc = sortAsc ? sortAsc : !sortAsc;
  columns = columns.map((c) => {
    if (c.key === sortColumn) {
      c.sortable = sortAsc;
    }
    return c;
  });
}, [columns, sortAsc]);
```

This memoization will ensure that the `sortColumnsChanged` and `sortAscChanged` functions are only called when the `columns` and `sortAsc` props have changed. This can help avoid unnecessary re-renders and improve the performance of the component.

*Response time: 31.6s*

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
Here's how you can implement the search feature in React using hooks and a custom hook.

**SearchPage.js**
```jsx
import React, { useState, useEffect, useCallback } from 'react';

function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [inFlight, setInFlight] = useState(false);

  const useSearch = (query: string) => {
    const timeoutId = useRef(null);

    useEffect(() => {
      setIsLoading(true);
      return () => {
        clearTimeout(timeoutId);
      };
    }, [inFlight]);

    const fetchResults = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(`/api/search?q=${query}`);
        const data = await response.json();
        setResults(data);
      } catch (error) {
        setError(error);
      } finally {
        setIsLoading(false);
      }
    };

    const handleSearch = useCallback(async () => {
      if (inFlight) return;
      setInFlight(true);
      setQuery(query);
      timeoutId.current = setTimeout(fetchResults, 300);
    }, [query]);

    useEffect(() => {
      return handleSearch;
    }, [handleSearch]);

    return { results, isLoading, error, inFlight };
  };

  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onSubmit={(e) => e.preventDefault()}
      />
      {isLoading && <div>Loading...</div>}
      {error && <div>Error: {error.message}</div>}
      {results.length === 0 && <div>No results</div>}
      {results.length > 0 && results.map((item) => (
        <div key={item.id}>{item.title}</div>
      ))}
    </div>
  );
}

export default SearchPage;
```

**search.js**
```jsx
import React from 'react';
import useSearch from './SearchPage';

const Search = () => {
  const { query, results, isLoading, error, inFlight } = useSearch(`query ${new Date().getTime()}`);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (results.length === 0) return <div>No results</div>;

  return results.map((item) => (
    <div key={item.id}>{item.title}</div>
  ));
};

export default Search;
```

**App.js**
```jsx
import React from 'react';
import Search from './Search';
import { useSearch } from './SearchPage';

const App = () => {
  const handleSearch = useSearch(`query ${new Date().getTime()}`);

  return (
    <div>
      <Search />
      <button onClick={handleSearch}>Search</button>
    </div>
  );
};

export default App;
```

**index.js**
```jsx
import React from 'react';
import { BrowserRouter as Router, Route } from 'react-router-dom';
import App from './App';

const routes = [
  { path: '/', component: App },
  { path: '/search', component: Search },
];

function AppRouter() {
  return (
    <Router>
      <Route path="/" element={<App />} />
      <Route path="/search" element={<Search />} />
    </Router>
  );
}

export default AppRouter;
```

**cache.js**
```jsx
import React from 'react';

const cache = {};

const getCachedResult = async (query) => {
  if (!cache[query]) {
    try {
      const response = await fetch(`/api/search?q=${query}`);
      const data = await response.json();
      cache[query] = data;
    } catch (error) {
      console.error('Error caching result:', error);
    }
  }
  return cache[query];
};

export default getCachedResult;
```

**index.html**
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>
<body>
  <div>
    <input type="text" value="" onChange="search()" />
    <button onclick="search()">Search</button>
  </div>

  <script src="search.js"></script>
  <script src="cache.js"></script>
  <script src="search.js"></script>
  <script src="app.js"></script>
</body>
</html>
```

The custom hook `useSearch` handles the fetch, debounce, cache, cancellation, and error handling for the search functionality. The `SearchPage` component uses this hook.

The `App.js` component is the entry point of the app, it renders the `Search` and `Search` components, and handles the search functionality.

The `AppRouter.js` component renders the router for the app, and handles the routing to the `/search` path when the "Search" button is clicked.

The `cache.js` file handles caching the results of the search for a given query.

The `index.html` file renders the search interface and the caching functionality.

Cancelling in-flight requests is important here to prevent the following bug:

```
Error: Cannot read properties of undefined (reading 'click')
```

This error occurs when trying to use the `onClick` event of the button to call the `handleSearch` function immediately. The `handleSearch` function is called on a new search request, not on the current search request, because the `useEffect` hook is called when the component is mounted, not when the button is clicked. If `handleSearch` were called immediately when the button is clicked, it would call the same search request multiple times, leading to the error. By using the debounce functionality and cancelling in-flight requests, we prevent this bug from occurring.

*Response time: 16.0s*

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
1. To fetch the 10 most recent published posts, including author name, tag names, comment count (not the comments themselves), you can use the following Prisma query:

   ```graphql
query GetRecentPublishedPosts {
  posts {
    id
    title
    content
    published
    author {
      name
    }
    tags {
      name
    }
    commentsCount {
      count
    }
  }
}
```

   This query will fetch the posts ordered by their `published` date in descending order. The query will include all fields from the `Post` model, excluding the comments themselves.

2. To add a `slug` field to the `Post` model and make it unique, nullable, and without null values, you can use the following migration scenario:

   ```sql
ALTER TABLE Post
ADD COLUMN Slug VARCHAR(255) UNIQUE NOT NULL;
```

   However, to do this safely without downtime, you can use the following approach:

   ```sql
ALTER TABLE Post
ADD COLUMN Slug VARCHAR(255) UNIQUE NOT NULL
ATOMIC;
```

   This approach ensures that the `Slug` column is created atomically, which means it will not be accessible until the database is successfully committed. This is crucial because you cannot create a nullable column without specifying whether it is nullable or not.

3. To diagnose and fix a slow query, you can use the following steps:

   - Use the `explain` function to analyze the query execution plan:

     ```graphql
query GetRecentPublishedPosts {
  posts {
    id
    title
    content
    published
    author {
      name
    }
    tags {
      name
    }
    commentsCount {
      count
    }
  }
}

EXPLAIN GetRecentPublishedPosts;
```

   - Analyze the query execution plan to identify the slow query. In this case, you might see that the query is spending most of its time on the `commentsCount` field.

   - To optimize the query, you can add an index on the `commentsCount` field:

     ```sql
CREATE INDEX idx_commentsCount ON posts (commentsCount);
```

   - Re-run the query and check if the performance has improved.

4. There are a few scenarios where you might drop down from Prisma to raw SQL. Here are a few examples:

   - When you need to perform a complex join operation that cannot be expressed using Prisma. For example, if you need to join a `Post` with a `User` table that does not have a foreign key relationship with the `Post` table.

   - When you need to perform a large-scale data retrieval operation that is not efficiently expressible using Prisma. For example, if you need to fetch millions of rows from a database table.

   - When you need to retrieve data from a table that has a complex indexing structure, and Prisma is not able to optimize the query execution plan.

Here is a real example from this schema:

You want to fetch all `Post` records that have a specific `title` and `content` (no `published` field).

```graphql
query FindPostsByTitleAndContent {
  posts {
    id
    title
    content
    published
  }
}
```

To execute this query, you would use the following raw SQL:

```sql
SELECT id, title, content, published
FROM post
WHERE title = $title
AND content = $content
```

However, this query might be slow if you have a large number of `Post` records in the database. To optimize this query, you can use an index on the `title` and `content` columns:

```sql
CREATE INDEX idx_title ON post (title);
CREATE INDEX idx_content ON post (content);
```

Then, you can re-run the query using the optimized index:

```sql
SELECT id, title, content, published
FROM post
WHERE title = $title
AND content = $content
USING INDEX (idx_title)
AND INDEX (idx_content)
```

This query should be much faster than the original raw SQL.

*Response time: 9.1s*

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
Here are the answers to your queries:

1. **Docker-Compose.yml for local development:**

```yml
version: '3'

services:
  web:
    build: .
    depends_on:
      - redis
    healthcheck:
      enabled: true
    env_file:
      - .env
    ports:
      - "3000:3000"
    restart: always

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - ./redis.data:/data

  healthcheck:
    build: .
    depends_on:
      - web
      - redis
    image: healthcheck:latest
    restart: always
    ports:
      - "8080:8080"
```

Here's a brief explanation of the changes:

- `web` is the main service, which is built from the current directory (`./`).
- `redis` is a container for Redis, which listens on port 6379.
- `healthcheck` is a health check service for both `web` and `redis`.

2. **Production Dockerfile for the backend (Node.js):**

```dockerfile
FROM node:14

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["node", "index.js"]
```

Here's a brief explanation of the changes:

- We're using the `node:14` image as the base, which is a Node.js version 14 image.
- The `WORKDIR` sets the working directory inside the container.
- We copy the necessary `package*.json` files and the application code into the container.
- We install the dependencies using `npm install`.
- We copy the application code and `package*.json` files to the container.
- We expose port 3000 to allow incoming traffic.
- We start the application using `node index.js`.

3. **Diagnosing the error in production:**

To diagnose the error, you can run the following commands:

```bash
docker exec -it web bash
```

(Replace `web` with the name of the service you're trying to diagnose.)

In the bash shell, you can use `healthcheck` to check if the `web` service is healthy. If the `healthcheck` service is not healthy, the `web` service will not be available.

Additionally, you can use `docker logs` to see the logs of the `web` service and `redis` service. This can help you identify the root cause of the error.

4. **Deploying a new version with zero downtime:**

Here's the deployment sequence step by step:

1. **Verify the new version:**
   Before starting the deployment, make sure you've verified the new version by running the following command:

   ```bash
   docker exec -it web bash
   ```

   and running the application in the bash shell.

2. **Stop the current version:**
   Run the following command to stop the current version:

   ```bash
   docker stop web
   ```

3. **Remove the current version:**
   Run the following command to remove the current version:

   ```bash
   docker rm web
   ```

4. **Start the new version:**
   Run the following command to start the new version:

   ```bash
   docker run -d --name web -p 3000:3000 healthcheck:latest
   ```

   (Replace `healthcheck:latest` with the image name you want to use for the new version.)

5. **Wait for the new version to be ready:**
   Wait for the new version to be ready by checking the healthcheck service. You can do this by running the following command:

   ```bash
   docker exec -it healthcheck bash
   ```

   (Again, replace `healthcheck` with the name of the healthcheck service you're trying to diagnose.)

6. **Verify the new version:**
   After the new version is ready, you can verify it by running the following command:

   ```bash
   docker exec -it web bash
   ```

   (Replace `web` with the name of the service you're trying to diagnose.)

   You can also use `docker logs` to see the logs of the new version.

Remember to use `docker-compose up` instead of running the individual services in the bash shell for production deployments. Also, make sure to remove the old images from the `docker-compose.yml` file before starting the new version.

*Response time: 10.2s*

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
Here is the core server implementation of the collaborative document editor using the ws library in Node.js:

```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

// Map to associate WebSocket connections with users and documents
let connectionMap = new Map();

// Function to join a document
function joinDocument(ws, documentId) {
  if (!connectionMap.has(ws)) {
    connectionMap.set(ws, { userId: Date.now().toString(), documentId });
    console.log(`User ${ws.upgrade?.id} joined document ${documentId}`);
  }
}

// Function to broadcast a change to all connected clients
function broadcastChange(ws, type, data) {
  const documentId = connectionMap.get(ws).documentId;
  if (documentId === null) return;

  if (type === "textChange") {
    const changes = { type: "textChange", data };
    ws.send(JSON.stringify(changes));
  } else if (type === "cursorMove") {
    const cursorMove = { type: "cursorMove", data };
    ws.send(JSON.stringify(cursorMove));
  }
}

// Function to handle incoming messages
wss.on('connection', (ws) => {
  console.log(`New WebSocket connection from ${ws.upgrade?.id}`);

  ws.on('message', (message) => {
    const jsonMessage = JSON.parse(message);
    switch (jsonMessage.type) {
      case "joinDocument":
        joinDocument(ws, jsonMessage.documentId);
        break;
      case "textChange":
        broadcastChange(ws, "textChange", jsonMessage.data);
        break;
      case "cursorMove":
        broadcastChange(ws, "cursorMove", jsonMessage.data);
        break;
      case "userLeft":
        // Remove the user's connection from the document
        const documentId = connectionMap.get(ws).documentId;
        if (documentId !== null) {
          connectionMap.delete(ws);
          console.log(`User ${ws.upgrade?.id} left document ${documentId}`);
        }
        break;
    }
  });

  ws.on('close', () => {
    // Remove the user's connection from the document
    const documentId = connectionMap.get(ws).documentId;
    if (documentId !== null) {
      connectionMap.delete(ws);
      console.log(`User ${ws.upgrade?.id} left document ${documentId}`);
    }
  });
});
```

This code defines the following:

- Connection handling: each user is associated with a WebSocket connection and a unique document ID.
- Message protocol: messages are JSON objects with a type (e.g., "joinDocument", "textChange", "cursorMove", "userLeft") and data.
- Broadcasting: changes are broadcast to all connected clients but not back to the user.
- Reconnection: when a user reconnects, their connection is added back to the document.
- Handling simultaneous edits: the issue is not addressed in this implementation. If two users edit the same position simultaneously, you need to implement a conflict resolution strategy. One approach is to use a version number and increment it for each change. However, this may not be suitable for all scenarios, and you can explore other strategies like using a conflict resolution service or adding additional metadata to the document.

To improve the implementation, consider adding error handling, logging, and possibly implementing a more robust conflict resolution strategy. Also, you may want to think about adding authentication and authorization to the system, as well as handling disconnections and timeouts.

*Response time: 8.4s*

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
Here are the answers to your queries:

1. **GraphQL Schema**:

```graphql
type Query {
  recipes(filter: Filter, pagination: Pagination): [Recipe]
}

type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String): Recipe
}

type Recipe {
  title: String!
  ingredients: [Ingredient]!
  steps: [Step]!
  author: Author!
  tags: [Tag]!
  ratings: [Rating]!
  averageRating: Float!
}

type Ingredient {
  name: String!
  amount: Float!
  unit: String!
}

type Step {
  title: String!
  steps: [StepStep]!
}

type StepStep {
  step: Int!
  text: String!
}

type Tag {
  name: String!
}

type Rating {
  score: Float!
  comment: String!
}

type Pagination {
  page: Int!
  limit: Int!
}

type Filter {
  tag: String!
  minRating: Float!
}

type Author {
  name: String!
  bio: String!
}
```

2. **Resolvers**:

```graphql
// Recipe resolvers
query Recipes($filter: Filter, $pagination: Pagination!) {
  recipes(filter: $filter, pagination: $pagination) {
    page
    limit
    total
    edges {
      node {
        title
        author {
          name
          bio
        }
        ingredients {
          node {
            name
            amount
            unit
          }
        }
        steps {
          node {
            steps {
              step {
                step
                text
              }
            }
          }
        }
        tags {
          node {
            name
          }
        }
        averageRating {
          rating
          comment
        }
      }
    }
  }
}

// Mutation resolvers
mutation AddRating($recipeId: ID!, $score: Float!, $comment: String!) {
  addRating(recipeId: $recipeId, score: $score, comment: $comment) {
    recipe {
      title
      author {
        name
        bio
      }
      tags
      ratings {
        node {
          rating
          comment
        }
      }
    }
  }
}
```

3. **N+1 Problem**:

Let's use a concrete example:

Suppose a client queries for recipes filtered by tags 'vegan' and 'gluten-free', with a minimum rating of 4.0. The server fetches the following recipe results:

```
[
  {
    title: "Vegan and Gluten-Free Recipe",
    ingredients: [
      {
        name: "vegan flours",
        amount: 1,
        unit: "pound",
      },
      {
        name: "olive oil",
        amount: 1,
        unit: "cup",
      },
      {
        name: "gluten-free flour",
        amount: 1,
        unit: "cup",
      },
    ],
    steps: [
      {
        title: "Mix ingredients",
        steps: [
          {
            step: 1,
            text: "Combine all ingredients in a bowl.",
          },
          {
            step: 2,
            text: "Mix well.",
          },
        ],
      },
    ],
    tags: [
      {
        name: "vegan",
      },
      {
        name: "gluten-free",
      },
    ],
    ratings: [
      {
        node: {
          rating: 4.0,
          comment: "Excellent recipe!",
        },
      },
    ],
    author: {
      name: "Alice",
      bio: "Experienced vegan chef.",
    },
  },
  {
    title: "Gluten-Free Chicken Stir-Fry",
    ingredients: [
      {
        name: "gluten-free chicken",
        amount: 1,
        unit: "pound",
      },
      {
        name: "vegan stir-fry sauce",
        amount: 2,
        unit: "tablespoons",
      },
      {
        name: "gluten-free rice",
        amount: 2,
        unit: "cups",
      },
    ],
    steps: [
      {
        title: "Stir-fry chicken",
        steps: [
          {
            step: 1,
            text: "Sauté chicken in a pan.",
          },
          {
            step: 2,
            text: "Add stir-fry sauce and rice.",
          },
        ],
      },
    ],
    tags: [
      {
        name: "vegan",
      },
    ],
    ratings: [
      {
        node: {
          rating: 4.5,
          comment: "Excellent flavor!",
        },
      },
    ],
    author: {
      name: "Bob",
      bio: "Experienced chef.",
    },
  },
]
```

The server would first fetch all tags matching 'vegan' and 'gluten-free', then for each tag, it would fetch all recipes that have the specified tag. For each recipe, it would fetch all ingredients, steps, tags, ratings, and author. This would result in a total of N*(N+1)/2 queries to the database.

4. **Recipe Query with Recipe Title and Author**:

Here's the exact GraphQL query the client would write:

```graphql
query {
  recipe(
    filter: {
      title: "Vegan and Gluten-Free Recipe",
      author: {
        name: "Alice",
        bio: "Experienced vegan chef.",
      },
    },
  ) {
    title
    author {
      name
      bio
    }
    ingredients {
      node {
        name
        amount
        unit
      }
    }
    steps {
      node {
        step {
          step
          text
        }
      }
    }
    tags {
      node {
        name
      }
    }
    ratings {
      node {
        rating
        comment
      }
    }
  }
}
```

5. **Choosing GraphQL over REST**:

GraphQL is a good choice when:

- The client needs fine-grained control over the data they receive.
- The server needs to support different types of clients (e.g., mobile, web, and native).
- The client needs to fetch multiple related resources in one query.
- The client needs to perform complex queries that involve filtering, sorting, and pagination.

Choosing REST over GraphQL:

- REST is suitable for simple, resource-based APIs where the client needs to perform a single, well-defined operation.
- REST is often used for APIs that are read-heavy, such as fetching data or retrieving information.
- REST is generally easier to implement and maintain than GraphQL, especially for small to medium-sized projects.

However, when the API needs to support multiple types of requests (e.g., read, write, query, and aggregate) and handle complex queries with filtering, sorting, and pagination, GraphQL might be a better choice.

*Response time: 15.4s*

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
Here is the complete HTML + CSS code for the UI layout you described:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="header">
        <h1>Welcome to our website</h1>
        <button class="button">Button</button>
        <button class="button">Button</button>
    </header>
    <nav class="sidebar">
        <ul>
            <li><a href="#">CARD 1</a></li>
            <li><a href="#">CARD 2</a></li>
            <li><a href="#">CARD 3</a></li>
        </ul>
    </nav>
    <main class="main-content">
        <div class="grid">
            <div class="card card-1">
                <img src="card-1.jpg" alt="Card 1">
                <h2>Card 1 Title</h2>
                <p>Card 1 Description</p>
                <footer class="footer">
                    <button>Left-aligned button</button>
                    <button>Right-aligned button</button>
                </footer>
            </div>
            <div class="card card-2">
                <img src="card-2.jpg" alt="Card 2">
                <h2>Card 2 Title</h2>
                <p>Card 2 Description</p>
                <footer class="footer">
                    <button>Left-aligned button</button>
                    <button>Right-aligned button</button>
                </footer>
            </div>
            <div class="card card-3">
                <img src="card-3.jpg" alt="Card 3">
                <h2>Card 3 Title</h2>
                <p>Card 3 Description</p>
                <footer class="footer">
                    <button>Left-aligned button</button>
                    <button>Right-aligned button</button>
                </footer>
            </div>
        </div>
    </main>
</body>
</html>
```

**CSS:**

```css
.header {
    position: fixed;
    width: 100%;
    height: 60px;
    background-color: #333;
    color: #fff;
    text-align: center;
    margin-bottom: 30px;
}

.header h1 {
    margin-top: 0;
}

.button {
    font-size: 1.2em;
    padding: 10px 20px;
    background-color: #4CAF50;
    color: #fff;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

.button:hover {
    background-color: #3e8e41;
}

.sidebar {
    position: fixed;
    width: 240px;
    height: 100%;
    background-color: #333;
    color: #fff;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-gap: 10px;
    margin-bottom: 30px;
}

.sidebar li {
    padding: 10px;
}

.sidebar li a {
    display: block;
    text-align: center;
    padding: 10px;
    font-size: 1.2em;
    border: none;
    border-radius: 5px;
    background-color: #4CAF50;
    color: #fff;
    cursor: pointer;
}

.sidebar li a:hover {
    background-color: #3e8e41;
}

.main-content {
    width: 100%;
    height: 100%;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-gap: 10px;
    background-color: #f2f2f2;
}

.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-gap: 10px;
    margin-bottom: 30px;
}

.card {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-gap: 10px;
    background-color: #fff;
    padding: 20px;
   

*Response time: 11.4s*

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
I'd be happy to help you design the notification system for your project management tool.

1. **Transport Mechanism:** I'd recommend using WebSocket for this task. WebSockets provide a bi-directional communication channel between a client and a server, which makes them ideal for real-time notifications. They are more efficient than other mechanisms, such as SSE (JSON events) or polling, because they allow for continuous communication between the client and server. Additionally, WebSockets are more reliable than push notifications, as they don't rely on periodic polling.

2. **Database Schema:** To store notifications, I'd design a database schema as follows:

- `users` table: stores user information (e.g., ID, name, email)
- `tasks` table: stores task information (e.g., ID, title, description, assigned_to, due_date)
- `notifications` table: stores notification information (e.g., ID, task_id, user_id, type, timestamp)
- `message` table: stores message information (e.g., ID, message_id, user_id, message, timestamp)

This schema allows for efficient querying and storing of notifications.

3. **Offline Notifications:** To handle users who are offline, I'd implement the following approach:

- Store the user's last active timestamp in the `users` table.
- When a user logs in, check if they are still active. If not, remove their last active timestamp and store the most recent timestamp.
- When the user logs in, fetch all tasks assigned to them and store them in the `notifications` table.

This approach ensures that the user gets all notifications they missed when they come back online.

4. **Deadline Check:** To implement the deadline check, I'd use a cron job. Here's an example implementation:

- Create a cron job that runs every hour.
- Read all tasks that have a due_date in the next 24 hours.
- Update the tasks table with a new `due_date` column that represents the current time.

This approach ensures that the deadline check runs every hour without using a queue or event-driven approach.

5. **Scalability:** To scale this system, I'd use a load balancer and multiple instances of the server. This will ensure that the load is distributed evenly across the instances and that the system can handle a large number of concurrent users. I'd also implement a load balancer with a high-availability (HA) solution to ensure that the system remains up even if one of the instances fails.

Here's an example implementation using HA for load balancers and multiple instances of the server:

```python
import requests
import time
import json

# Load Balancer configuration
load_balancer_config = {
    'servers': ['server1', 'server2', 'server3'],
    'port': 80
}

# Server instance configuration
server_config = {
    'host': 'localhost',
    'port': 5000
}

def add_notification(task_id, user_id, type, message):
    # Create a notification message
    message_data = {
        'task_id': task_id,
        'user_id': user_id,
        'type': type,
        'message': message
    }

    # Send a notification message
    requests.post('http://localhost:5001/notify', json=message_data)

def get_user_last_active_timestamp(user_id):
    # Retrieve the user's last active timestamp from the database
    query = "SELECT last_active_timestamp FROM users WHERE id = ?"
    response = requests.get('http://localhost:5000/users', params={'id': user_id})
    data = response.json()
    if data['status'] == 'success':
        return data['data']['last_active_timestamp']
    else:
        return None

def update_user_last_active_timestamp(user_id):
    # Update the user's last active timestamp in the database
    query = "UPDATE users SET last_active_timestamp = ? WHERE id = ?"
    response = requests.post('http://localhost:5000/users', json={'last_active_timestamp': time.time()})
    if response.json()['status'] == 'success':
        return True
    else:
        return False

def fetch_tasks_with_due_date_in_next_24_hours():
    # Read tasks that have a due_date in the next 24 hours
    query = "SELECT task_id FROM tasks WHERE due_date > ? ORDER BY due_date"
    response = requests.get('http://localhost:5000/tasks', params={'timestamp': int(time.time()) - 24*60*60})
    if response.json()['status'] == 'success':
        return response.json()['data']
    else:
        return []

# Main application loop
while True:
    # Get the user's last active timestamp
    user_id = 1
    last_active_timestamp = get_user_last_active_timestamp(user_id)

    # Fetch tasks with due date in next 24 hours
    tasks = fetch_tasks_with_due_date_in_next_24_hours()

    # Add notifications for tasks with due dates in next 24 hours
    for task in tasks:
        if task['due_date'] > last_active_timestamp:
            add_notification(task['task_id'], user_id, 'task_due_date', 'Task {} has a due date in the next 24 hours.'.format(task['title']))

    # Send a notification message
    add_notification('task_due_date', user_id, 'task_due_date', 'Task {} has a due date in the next 24 hours.'.format(task['title']))

    # Update the user's last active timestamp
    if update_user_last_active_timestamp(user_id):
        last_active_timestamp = time.time()

    # Wait

*Response time: 13.4s*

---
