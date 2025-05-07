import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Switch } from "../../../components/ui/switch";
import { Checkbox } from "../../../components/ui/checkbox";
import { Loader2, ArrowLeft, Save } from "lucide-react";
import { getUser, createUser, updateUser, getRoles, getPermissions } from '../api/usersApi';
import { UserCreate, UserUpdate, Role } from '../types';
import { useToast } from "../../../hooks/use-toast";
import PermissionMatrix from '../components/PermissionMatrix';
import AuditLogView from '../components/AuditLogView';
import { useTranslation } from 'react-i18next';

const UserForm: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEditMode = !!id;
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    active: true
  });
  
  const [selectedRoles, setSelectedRoles] = useState<number[]>([]);
  const [selectedPermissions, setSelectedPermissions] = useState<{ id: number; start_date?: Date; end_date?: Date }[]>([]);
  const [formErrors, setFormErrors] = useState<{ [key: string]: string }>({});
  
  const { data: userData, isLoading: isLoadingUser } = useQuery({
    queryKey: ['user', id],
    queryFn: () => getUser(Number(id)),
    enabled: isEditMode
  });
  
  const { data: roles = [], isLoading: isLoadingRoles } = useQuery({
    queryKey: ['roles'],
    queryFn: getRoles
  });
  
  const { data: permissions = [], isLoading: isLoadingPermissions } = useQuery({
    queryKey: ['permissions'],
    queryFn: getPermissions
  });
  
  const createUserMutation = useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast({
        title: t('User created'),
        description: t('The user has been successfully created.'),
      });
      navigate('/users');
    },
    onError: (error) => {
      toast({
        title: t('Error'),
        description: t('Failed to create user. Please try again.'),
        variant: 'destructive',
      });
      console.error('Create error:', error);
    }
  });
  
  const updateUserMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: UserUpdate }) => updateUser(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.invalidateQueries({ queryKey: ['user', id] });
      toast({
        title: t('User updated'),
        description: t('The user has been successfully updated.'),
      });
      navigate('/users');
    },
    onError: (error) => {
      toast({
        title: t('Error'),
        description: t('Failed to update user. Please try again.'),
        variant: 'destructive',
      });
      console.error('Update error:', error);
    }
  });
  
  useEffect(() => {
    if (userData) {
      setFormData({
        name: userData.name,
        email: userData.email,
        password: '',
        active: userData.active
      });
      
      setSelectedRoles(userData.roles.map(role => role.id));
      
      const permissionsFromRoles = userData.roles.flatMap(role => role.permissions);
      const uniquePermissions = permissionsFromRoles.filter((permission, index, self) => 
        index === self.findIndex(p => p.id === permission.id)
      );
      
      setSelectedPermissions(uniquePermissions.map(permission => ({
        id: permission.id,
        start_date: permission.start_date ? new Date(permission.start_date) : undefined,
        end_date: permission.end_date ? new Date(permission.end_date) : undefined
      })));
    }
  }, [userData]);
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    if (formErrors[name]) {
      setFormErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };
  
  const validateForm = () => {
    const errors: { [key: string]: string } = {};
    
    if (!formData.name.trim()) {
      errors.name = t('Name is required');
    }
    
    if (!formData.email.trim()) {
      errors.email = t('Email is required');
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = t('Email is invalid');
    }
    
    if (!isEditMode && !formData.password.trim()) {
      errors.password = t('Password is required');
    } else if (!isEditMode && formData.password.length < 8) {
      errors.password = t('Password must be at least 8 characters');
    }
    
    if (selectedRoles.length === 0) {
      errors.roles = t('At least one role must be selected');
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    if (isEditMode) {
      const updateData: UserUpdate = {
        name: formData.name,
        email: formData.email,
        active: formData.active,
        role_ids: selectedRoles
      };
      
      if (formData.password.trim()) {
        updateData.password = formData.password;
      }
      
      updateUserMutation.mutate({ id: Number(id), data: updateData });
    } else {
      const createData: UserCreate = {
        name: formData.name,
        email: formData.email,
        password: formData.password,
        active: formData.active,
        role_ids: selectedRoles
      };
      
      createUserMutation.mutate(createData);
    }
  };
  
  const isLoading = isLoadingUser || isLoadingRoles || isLoadingPermissions || 
                   createUserMutation.isPending || updateUserMutation.isPending;
  
  return (
    <div className="container mx-auto py-6">
      <div className="flex items-center mb-6">
        <Button 
          variant="outline" 
          onClick={() => navigate('/users')}
          className="mr-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          {t('Back')}
        </Button>
        <div>
          <h1 className="text-3xl font-bold">
            {isEditMode ? t('Edit User') : t('New User')}
          </h1>
          <p className="text-gray-500">
            {isEditMode ? t('Update user details and permissions') : t('Create a new user account')}
          </p>
        </div>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>{t('User Information')}</CardTitle>
              <CardDescription>{t('Basic user account details')}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid w-full items-center gap-1.5">
                <Label htmlFor="name">{t('Name')}</Label>
                <Input
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder={t('Enter full name')}
                  disabled={isLoading}
                />
                {formErrors.name && (
                  <p className="text-sm text-red-500">{formErrors.name}</p>
                )}
              </div>
              
              <div className="grid w-full items-center gap-1.5">
                <Label htmlFor="email">{t('Email')}</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder={t('Enter email address')}
                  disabled={isLoading}
                />
                {formErrors.email && (
                  <p className="text-sm text-red-500">{formErrors.email}</p>
                )}
              </div>
              
              <div className="grid w-full items-center gap-1.5">
                <Label htmlFor="password">
                  {isEditMode ? t('New Password (leave blank to keep current)') : t('Password')}
                </Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder={isEditMode ? t('Enter new password (optional)') : t('Enter password')}
                  disabled={isLoading}
                />
                {formErrors.password && (
                  <p className="text-sm text-red-500">{formErrors.password}</p>
                )}
              </div>
              
              <div className="flex items-center space-x-2">
                <Switch
                  id="active"
                  name="active"
                  checked={formData.active}
                  onCheckedChange={(checked) => 
                    setFormData(prev => ({ ...prev, active: checked }))
                  }
                  disabled={isLoading}
                />
                <Label htmlFor="active">{t('Active Account')}</Label>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>{t('Roles')}</CardTitle>
              <CardDescription>{t('Assign roles to this user')}</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoadingRoles ? (
                <div className="flex justify-center py-4">
                  <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
              ) : (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {roles.map((role: Role) => (
                      <div key={role.id} className="flex items-center space-x-2">
                        <Checkbox
                          id={`role-${role.id}`}
                          checked={selectedRoles.includes(role.id)}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              setSelectedRoles([...selectedRoles, role.id]);
                              
                              if (formErrors.roles) {
                                setFormErrors(prev => {
                                  const newErrors = { ...prev };
                                  delete newErrors.roles;
                                  return newErrors;
                                });
                              }
                            } else {
                              setSelectedRoles(selectedRoles.filter(id => id !== role.id));
                            }
                          }}
                          disabled={isLoading}
                        />
                        <Label htmlFor={`role-${role.id}`}>{role.name}</Label>
                      </div>
                    ))}
                  </div>
                  {formErrors.roles && (
                    <p className="text-sm text-red-500 mt-2">{formErrors.roles}</p>
                  )}
                </>
              )}
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>{t('Permissions')}</CardTitle>
              <CardDescription>{t('Assign specific permissions with time bounds')}</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoadingPermissions ? (
                <div className="flex justify-center py-4">
                  <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
              ) : (
                <PermissionMatrix
                  permissions={permissions}
                  selectedPermissions={selectedPermissions}
                  onChange={setSelectedPermissions}
                />
              )}
            </CardContent>
          </Card>
          
          {isEditMode && (
            <Card>
              <CardHeader>
                <CardTitle>{t('Audit Trail')}</CardTitle>
                <CardDescription>{t('Recent activity for this user')}</CardDescription>
              </CardHeader>
              <CardContent>
                <AuditLogView 
                  auditLogs={[]} 
                  title="User Activity" 
                  maxItems={5} 
                />
              </CardContent>
            </Card>
          )}
          
          <div className="flex justify-end gap-2 mt-6">
            <Button 
              variant="outline" 
              onClick={() => navigate('/users')}
              disabled={isLoading}
            >
              {t('Cancel')}
            </Button>
            <Button 
              type="submit" 
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {t('Saving...')}
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  {isEditMode ? t('Update User') : t('Create User')}
                </>
              )}
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default UserForm;
