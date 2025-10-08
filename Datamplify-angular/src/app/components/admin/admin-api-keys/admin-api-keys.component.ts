import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NgbModal, NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-admin-api-keys',
  standalone: true,
  imports: [CommonModule, FormsModule, NgbModule],
  templateUrl: './admin-api-keys.component.html',
  styleUrl: './admin-api-keys.component.scss'
})
export class AdminApiKeysComponent implements OnInit {
  apiKeys: any[] = [];
  
  newKey = {
    name: '',
    provider: '',
    key: ''
  };

  providers = [
    { value: 'google', label: 'Google AI', icon: 'fa-google' },
    { value: 'perplexity', label: 'Perplexity AI', icon: 'fa-brain' },
    { value: 'openai', label: 'OpenAI', icon: 'fa-robot' },
    { value: 'aws', label: 'AWS', icon: 'fa-aws' },
    { value: 'azure', label: 'Azure', icon: 'fa-microsoft' }
  ];

  constructor(
    private modalService: NgbModal,
    private toastr: ToastrService
  ) {}

  ngOnInit() {
    this.loadApiKeys();
  }

  loadApiKeys() {
    // Mock data - replace with actual API call
    this.apiKeys = [
      {
        id: 1,
        name: 'Google AI Key',
        provider: 'google',
        key: 'AIzaSyAK2s3xUtZpRcuCCD8SbXqbp8OLNmbtz4c',
        maskedKey: 'AIza...tz4c',
        createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7),
        lastUsed: new Date(Date.now() - 1000 * 60 * 30),
        status: 'active'
      },
      {
        id: 2,
        name: 'Perplexity AI Key',
        provider: 'perplexity',
        key: 'pplx-abc123def456',
        maskedKey: 'pplx-...f456',
        createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 14),
        lastUsed: new Date(Date.now() - 1000 * 60 * 60),
        status: 'active'
      }
    ];
  }

  openAddKeyModal(content: any) {
    this.newKey = { name: '', provider: '', key: '' };
    this.modalService.open(content, { size: 'lg' });
  }

  addApiKey(modal: any) {
    if (!this.newKey.name || !this.newKey.provider || !this.newKey.key) {
      this.toastr.warning('Please fill in all fields', 'Warning');
      return;
    }

    const maskedKey = this.maskApiKey(this.newKey.key);
    this.apiKeys.push({
      id: this.apiKeys.length + 1,
      name: this.newKey.name,
      provider: this.newKey.provider,
      key: this.newKey.key,
      maskedKey: maskedKey,
      createdAt: new Date(),
      lastUsed: null,
      status: 'active'
    });

    this.toastr.success('API Key added successfully', 'Success');
    modal.close();
  }

  maskApiKey(key: string): string {
    if (key.length <= 8) return key;
    return key.substring(0, 4) + '...' + key.substring(key.length - 4);
  }

  copyToClipboard(key: string) {
    navigator.clipboard.writeText(key);
    this.toastr.success('API Key copied to clipboard', 'Success');
  }

  deleteKey(id: number) {
    this.apiKeys = this.apiKeys.filter(k => k.id !== id);
    this.toastr.success('API Key deleted', 'Success');
  }

  getProviderIcon(provider: string): string {
    const p = this.providers.find(pr => pr.value === provider);
    return p ? p.icon : 'fa-key';
  }

  getProviderLabel(provider: string): string {
    const p = this.providers.find(pr => pr.value === provider);
    return p ? p.label : provider;
  }
}
