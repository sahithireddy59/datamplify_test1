import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [CommonModule, RouterModule, NgbModule],
  templateUrl: './admin-layout.component.html',
  styleUrl: './admin-layout.component.scss'
})
export class AdminLayoutComponent implements OnInit {
  isSidebarCollapsed = false;
  currentUser: any = null;
  
  adminMenuItems = [
    {
      title: 'Dashboard',
      icon: 'fa fa-tachometer-alt',
      route: '/admin/dashboard',
      description: 'Overview and statistics'
    },
    {
      title: 'User Management',
      icon: 'fa fa-users',
      route: '/admin/users',
      description: 'Manage users and permissions'
    },
    {
      title: 'Role Management',
      icon: 'fa fa-user-shield',
      route: '/admin/roles',
      description: 'Manage roles and privileges'
    },
    {
      title: 'System Settings',
      icon: 'fa fa-cog',
      route: '/admin/settings',
      description: 'Configure system settings'
    },
    {
      title: 'Activity Logs',
      icon: 'fa fa-history',
      route: '/admin/logs',
      description: 'View system activity logs'
    },
    {
      title: 'API Keys',
      icon: 'fa fa-key',
      route: '/admin/api-keys',
      description: 'Manage API keys and credentials'
    }
  ];

  constructor(private router: Router) {}

  ngOnInit() {
    // Get current user from session/local storage
    const userStr = localStorage.getItem('currentUser');
    if (userStr) {
      this.currentUser = JSON.parse(userStr);
    }
  }

  toggleSidebar() {
    this.isSidebarCollapsed = !this.isSidebarCollapsed;
  }

  isActiveRoute(route: string): boolean {
    return this.router.url.includes(route);
  }

  logout() {
    // Clear session and navigate to login
    localStorage.removeItem('currentUser');
    sessionStorage.clear();
    this.router.navigate(['/login']);
  }

  navigateToWorkbench() {
    this.router.navigate(['/datamplify/dashboard']);
  }
}
