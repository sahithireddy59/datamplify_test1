import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { authGuard } from '../../auth.guard';

export const admin: Routes = [

  {
    path: 'datamplify', children: [

      {
        path: 'home',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./landingpage/landingpage.component').then((m) => m.LandingpageComponent)
      },
      {
        path: 'users/users-list',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./users-dashboard/users-dashboard.component').then((m) => m.UsersDashboardComponent)
      },
      {
        path: 'users/add-user',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./users-dashboard/users-dashboard.component').then((m) => m.UsersDashboardComponent)
      },
      {
        path: 'users/edit-user/:id',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./users-dashboard/users-dashboard.component').then((m) => m.UsersDashboardComponent)
      },
      {
        path: 'roles/roles-list',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./roles-dashboard/roles-dashboard.component').then((m) => m.RolesDashboardComponent)
      },
      {
        path: 'roles/add-role',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./roles-dashboard/roles-dashboard.component').then((m) => m.RolesDashboardComponent)
      },
      {
        path: 'dashboard/role-edit/:id1',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./roles-dashboard/roles-dashboard.component').then((m) => m.RolesDashboardComponent)
      },

      {
        path: 'update-password',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./update-password/update-password.component').then((m) => m.UpdatePasswordComponent),
      },

      {
        path: 'configure-page/configure',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./configure/configure.component').then((m) => m.ConfigureComponent),
      },

      {
        path: 'easyConnection',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./easy-connection/easy-connection.component').then((m) => m.EasyConnectionComponent),
      },

      {
        path: 'home/easyConnection',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./easy-connection/easy-connection.component').then((m) => m.EasyConnectionComponent),
      },

      {
        path: 'flowboardList',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./flowboard-list/flowboard-list.component').then((m) => m.FlowboardListComponent),
      },
      
      {
        path: 'taskplanList',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./taskplan-list/taskplan-list.component').then((m) => m.TaskplanListComponent),
      },

      {
        path: 'monitorList',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./monitor-list/monitor-list.component').then((m) => m.MonitorListComponent),
      },

      {
        path: 'flowboardList/flowboard',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./flowboard/flowboard.component').then((m) => m.FlowboardComponent),
      },

      {
        path: 'flowboardList/flowboard/:id1',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./flowboard/flowboard.component').then((m) => m.FlowboardComponent),
      },

      {
        path: 'taskplanList/taskplan',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./taskplan/taskplan.component').then((m) => m.TaskplanComponent),
      },

      {
        path: 'taskplanList/taskplan/:id1',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./taskplan/taskplan.component').then((m) => m.TaskplanComponent),
      },

      {
        path: 'monitorList/monitor/:id1',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./etl-monitor/etl-monitor.component').then((m) => m.EtlMonitorComponent),
      },

      {
        path: 'home/dashboard',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./etl-dashboard/etl-dashboard.component').then((m) => m.EtlDashboardComponent),
      },

      {
        path: 'home/dashboard1',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./dashboard/dashboard.component').then((m) => m.DashboardComponent),
      },

      {
        path: 'home/easyConnection1',
        canActivate: [authGuard],
        loadComponent: () =>
          import('./easy-connect/easy-connect.component').then((m) => m.EasyConnectComponent),
      },
    ]
  }
 ];

@NgModule({
  declarations: [],
  imports: [
    CommonModule,RouterModule.forChild(admin),
  ],
  exports:[RouterModule]
})
export class WorkbenchModule { 
  static routes = admin;


}
