import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-admin-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-settings.component.html',
  styleUrl: './admin-settings.component.scss'
})
export class AdminSettingsComponent {
  settings = {
    appName: 'Datamplify',
    appVersion: '1.0.0',
    maxUploadSize: '100',
    sessionTimeout: '30',
    enableAuditLog: true,
    enableEmailNotifications: true,
    maintenanceMode: false
  };

  saveSettings() {
    console.log('Saving settings:', this.settings);
    // TODO: Implement API call to save settings
  }
}
