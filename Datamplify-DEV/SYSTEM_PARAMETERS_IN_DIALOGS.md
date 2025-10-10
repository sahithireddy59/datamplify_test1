# ✅ System Parameters in All Dialog Boxes - Implementation Guide

## 🎯 **Goal:**
Show system parameters (like `$mpfilepath`, `$CURRENT_DATE`) in **ALL dialog boxes** where users can select parameters, under a "Project Parameters" section.

---

## 📋 **Where System Parameters Should Appear:**

### **1. Expression Editor (Data Flow)**
- When editing expressions in transformations
- Under "Project Parameters" tab
- Shows all 21 system parameters

### **2. Attribute Mapper**
- When mapping source to target columns
- Parameter selection dropdown
- System parameters available for selection

### **3. Transformation Properties**
- Router conditions
- Filter expressions
- Any field that accepts parameters

### **4. File Path Templates**
- CSV connection dynamic paths
- Looper file paths
- Any path configuration

---

## 🔧 **Implementation Steps:**

### **Step 1: Create a Shared Parameter Service**

**File:** `src/app/services/global-parameters.service.ts`

This service should:
1. Fetch system parameters from backend
2. Cache them for performance
3. Provide them to all components

**Already exists!** Just need to ensure it's being used everywhere.

### **Step 2: Update Backend API**

**Already Done!** ✅
- Backend returns system parameters in `/api/connections/global_parameters/`
- 21 system parameters always included
- Marked with `is_system: true`

### **Step 3: Add System Parameters to Dialog Components**

Need to update these components to show system parameters:

**Components to Update:**
1. **Expression Editor** (if it exists as a separate component)
2. **Parameter Selector** (shared component for parameter selection)
3. **Transformation Forms** (Router, Filter, etc.)
4. **Attribute Mapper**

---

## 💡 **Recommended Approach:**

### **Create a Shared Parameter Selector Component**

**File:** `src/app/shared/components/parameter-selector/parameter-selector.component.ts`

```typescript
import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { GlobalParametersService } from '../../../services/global-parameters.service';

@Component({
  selector: 'app-parameter-selector',
  template: `
    <div class="parameter-selector">
      <!-- Tabs -->
      <ul class="nav nav-tabs">
        <li class="nav-item">
          <a class="nav-link" [class.active]="activeTab === 'transforms'" 
             (click)="activeTab = 'transforms'">Transforms</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" [class.active]="activeTab === 'project'" 
             (click)="activeTab = 'project'">Project Parameters</a>
        </li>
      </ul>

      <!-- Project Parameters Tab -->
      <div *ngIf="activeTab === 'project'" class="parameter-list">
        <input type="text" class="form-control mb-2" 
               [(ngModel)]="searchText" placeholder="Search fields...">
        
        <!-- System Parameters Section -->
        <div class="param-section">
          <h6 class="text-muted">🔒 System Parameters</h6>
          <div *ngFor="let param of filteredSystemParams" 
               class="param-item" 
               (click)="selectParameter(param)">
            <i class="bi bi-gear-fill text-primary me-2"></i>
            <strong>\${{ param.parameter_name }}</strong>
            <small class="text-muted ms-2">{{ param.description }}</small>
          </div>
        </div>

        <!-- User Parameters Section -->
        <div class="param-section mt-3">
          <h6 class="text-muted">👤 User Parameters</h6>
          <div *ngFor="let param of filteredUserParams" 
               class="param-item" 
               (click)="selectParameter(param)">
            <i class="bi bi-tag-fill text-info me-2"></i>
            <strong>\${{ param.parameter_name }}</strong>
            <small class="text-muted ms-2">{{ param.description }}</small>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .param-item {
      padding: 8px 12px;
      cursor: pointer;
      border-radius: 4px;
      margin-bottom: 4px;
    }
    .param-item:hover {
      background-color: #f0f0f0;
    }
    .param-section {
      max-height: 300px;
      overflow-y: auto;
    }
  `]
})
export class ParameterSelectorComponent implements OnInit {
  @Output() parameterSelected = new EventEmitter<any>();
  
  activeTab: string = 'transforms';
  searchText: string = '';
  
  systemParameters: any[] = [];
  userParameters: any[] = [];
  
  get filteredSystemParams() {
    return this.systemParameters.filter(p => 
      p.parameter_name.toLowerCase().includes(this.searchText.toLowerCase()) ||
      p.description.toLowerCase().includes(this.searchText.toLowerCase())
    );
  }
  
  get filteredUserParams() {
    return this.userParameters.filter(p => 
      p.parameter_name.toLowerCase().includes(this.searchText.toLowerCase())
    );
  }

  constructor(private paramService: GlobalParametersService) {}

  ngOnInit() {
    this.loadParameters();
  }

  loadParameters() {
    this.paramService.getGlobalParameters().subscribe(response => {
      const allParams = response.data;
      this.systemParameters = allParams.filter((p: any) => p.is_system === true);
      this.userParameters = allParams.filter((p: any) => p.is_system !== true);
    });
  }

  selectParameter(param: any) {
    this.parameterSelected.emit(param);
  }
}
```

---

## 📍 **Where to Use This Component:**

### **1. In FlowBoard Transformations**

When user clicks on a field that accepts parameters:

```html
<!-- In transformation property dialog -->
<div class="modal" *ngIf="showParameterSelector">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h5>Select Parameter</h5>
      </div>
      <div class="modal-body">
        <app-parameter-selector 
          (parameterSelected)="onParameterSelected($event)">
        </app-parameter-selector>
      </div>
    </div>
  </div>
</div>
```

### **2. In Attribute Mapper**

For mapping expressions:

```html
<button (click)="showParameterSelector = true">
  <i class="bi bi-code"></i> Insert Parameter
</button>

<app-parameter-selector 
  *ngIf="showParameterSelector"
  (parameterSelected)="insertParameter($event)">
</app-parameter-selector>
```

### **3. In CSV Connection**

For file path templates:

```html
<input [(ngModel)]="dynamicFilePath" placeholder="File path">
<button (click)="showParams = true">📋 Parameters</button>

<app-parameter-selector 
  *ngIf="showParams"
  (parameterSelected)="insertIntoPath($event)">
</app-parameter-selector>
```

---

## 🎨 **UI Design (Like Screenshot):**

```
┌─────────────────────────────────────────────────┐
│ Expression Editor - ai (Data Flow)              │
├─────────────────────────────────────────────────┤
│ *PARAM_NAME_1 (varchar)                         │
│ ┌─────────────────────────────────────────────┐ │
│ │ Enter expression...                         │ │
│ │                                             │ │
│ │                                             │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ [Transforms ▼]  [Project Parameters]           │
│                                                 │
│ Search fields...                                │
│                                                 │
│ 🔒 System Parameters                           │
│ ⚙️ $mpfilepath          - Base file path       │
│ ⚙️ $CURRENT_DATE        - Current date         │
│ ⚙️ $CURRENT_YEAR        - Current year         │
│ ⚙️ $mptemppath          - Temp directory       │
│ ... (21 total)                                  │
│                                                 │
│ 👤 User Parameters                              │
│ 🏷️ $MY_PARAM           - Custom parameter     │
│                                                 │
│                        [Cancel]  [OK]           │
└─────────────────────────────────────────────────┘
```

---

## ✅ **Quick Implementation Checklist:**

### **Backend (Already Done!):**
- ✅ System parameters in `get_system_parameters()`
- ✅ API returns them in `/api/connections/global_parameters/`
- ✅ Marked with `is_system: true`

### **Frontend (To Do):**
- ⬜ Create shared `ParameterSelectorComponent`
- ⬜ Add to FlowBoard transformation dialogs
- ⬜ Add to Attribute Mapper
- ⬜ Add to CSV connection path editor
- ⬜ Add to any other parameter input fields

---

## 🔧 **Alternative: Simpler Approach**

If you don't want a separate component, add this to **each dialog** where parameters are needed:

```typescript
// In component.ts
systemParameters: any[] = [];
userParameters: any[] = [];

ngOnInit() {
  this.globalParamsService.getGlobalParameters().subscribe(response => {
    this.systemParameters = response.data.filter((p: any) => p.is_system === true);
    this.userParameters = response.data.filter((p: any) => p.is_system !== true);
  });
}
```

```html
<!-- In component.html -->
<div class="parameter-section">
  <h6>🔒 System Parameters</h6>
  <div *ngFor="let param of systemParameters" 
       (click)="insertParameter('$' + param.parameter_name)">
    ⚙️ ${{ param.parameter_name }} - {{ param.description }}
  </div>
</div>
```

---

## 📝 **Summary:**

**To show system parameters in all dialogs:**

1. ✅ **Backend Ready**: System parameters already available via API
2. ⬜ **Create Shared Component**: `ParameterSelectorComponent` 
3. ⬜ **Add to Dialogs**: Use component in all parameter selection dialogs
4. ⬜ **Test**: Verify parameters appear in FlowBoard, Mapper, CSV, etc.

**Result:** Users will see all 21 system parameters (like `$mpfilepath`, `$CURRENT_DATE`) in every dialog where they can select parameters!

---

**Next Step:** Would you like me to create the `ParameterSelectorComponent` and show you exactly where to add it in your existing FlowBoard/TaskPlan components?
