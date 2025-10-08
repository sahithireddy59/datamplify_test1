import { Route } from '@angular/router';
import { AuthenticationLayoutComponent } from './shared/layout-components/layouts/authentication-layout/authentication-layout.component';
import { authen } from './shared/routes/authenticationroutes';
import { workbench } from './shared/routes/workbenckroutes';
import { WorkbenchLayoutsComponent } from './shared/layout-components/layouts/workbench-layouts/workbench-layouts.component';
import { adminRoutes } from './components/admin/admin.routes';

export const App_Route: Route[] = [
      { path: '', redirectTo: 'authentication/login', pathMatch: 'full' },
      {
        path: '',
        loadComponent: () => import('../app/components/authentication/login/login.component').then((m) => m.LoginComponent),
      },
      { path: '', component: AuthenticationLayoutComponent, children: authen },
      { path: '', component: WorkbenchLayoutsComponent, children: workbench },
      { path: 'admin', children: adminRoutes },


    ]