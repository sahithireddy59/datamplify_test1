import { Routes } from '@angular/router';
import { AdminLayoutComponent } from './admin-layout/admin-layout.component';
import { AdminDashboardComponent } from './admin-dashboard/admin-dashboard.component';

export const adminRoutes: Routes = [
  {
    path: '',
    component: AdminLayoutComponent,
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        component: AdminDashboardComponent
      },
      {
        path: 'users',
        loadComponent: () => import('../workbench/users-dashboard/users-dashboard.component').then(m => m.UsersDashboardComponent)
      },
      {
        path: 'roles',
        loadComponent: () => import('../workbench/roles-dashboard/roles-dashboard.component').then(m => m.RolesDashboardComponent)
      },
      {
        path: 'settings',
        loadComponent: () => import('./admin-settings/admin-settings.component').then(m => m.AdminSettingsComponent)
      },
      {
        path: 'logs',
        loadComponent: () => import('./admin-logs/admin-logs.component').then(m => m.AdminLogsComponent)
      },
      {
        path: 'api-keys',
        loadComponent: () => import('./admin-api-keys/admin-api-keys.component').then(m => m.AdminApiKeysComponent)
      }
    ]
  }
];
