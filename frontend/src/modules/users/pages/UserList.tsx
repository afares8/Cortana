import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "../../../components/ui/table";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Badge } from "../../../components/ui/badge";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "../../../components/ui/card";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from "../../../components/ui/dropdown-menu";
import { 
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../../../components/ui/alert-dialog";
import { useToast } from "../../../hooks/use-toast";
import { Loader2, Search, MoreVertical, Plus, Edit, Trash, Lock, Key, Eye } from "lucide-react";
import { getUsers, deleteUser } from '../api/usersApi';
import { User } from '../types';
import { useTranslation } from 'react-i18next';

const UserList: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [userToDelete, setUserToDelete] = useState<User | null>(null);
  
  const { data: users = [], isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: getUsers
  });
  
  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast({
        title: t('User deleted'),
        description: t('The user has been successfully deleted.'),
      });
      setUserToDelete(null);
    },
    onError: (error) => {
      toast({
        title: t('Error'),
        description: t('Failed to delete user. Please try again.'),
        variant: 'destructive',
      });
      console.error('Delete error:', error);
    }
  });
  
  const filteredUsers = users.filter(user => 
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  const handleDeleteUser = () => {
    if (userToDelete) {
      deleteMutation.mutate(userToDelete.id);
    }
  };
  
  if (error) {
    return (
      <Card className="mx-auto max-w-6xl">
        <CardHeader>
          <CardTitle>{t('Users')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center p-8 text-center">
            <p className="text-red-500 mb-4">{t('Error loading users')}</p>
            <Button onClick={() => queryClient.invalidateQueries({ queryKey: ['users'] })}>
              {t('Try Again')}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <div className="bg-red-100 mx-auto max-w-6xl"> {/* Temporary background for debugging */}
      <Card className="mx-auto max-w-6xl">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>{t('Users')}</CardTitle>
            <CardDescription>{t('Manage user accounts, roles, and permissions.')}</CardDescription>
          </div>
          <Button onClick={() => navigate('/users/new')}>
            <Plus className="mr-2 h-4 w-4" />
            {t('New User')}
          </Button>
        </CardHeader>
        <CardContent>
          <div className="mb-4 relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
            <Input
              type="text"
              placeholder={t('Search users...')}
              className="pl-8"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          {isLoading ? (
            <div className="flex justify-center p-8">
              <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
            </div>
          ) : filteredUsers.length === 0 ? (
            <div className="text-center p-8 text-gray-500">
              {searchTerm ? t('No users match your search.') : t('No users found. Create your first user!')}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t('Name')}</TableHead>
                  <TableHead>{t('Email')}</TableHead>
                  <TableHead>{t('Status')}</TableHead>
                  <TableHead>{t('Roles')}</TableHead>
                  <TableHead className="text-right">{t('Actions')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell className="font-medium">{user.name}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      {user.active ? (
                        <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
                          {t('Active')}
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="bg-gray-100 text-gray-800 hover:bg-gray-100">
                          {t('Inactive')}
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {user.roles.map((role) => (
                          <Badge key={role.id} variant="outline">
                            {role.name}
                          </Badge>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreVertical className="h-4 w-4" />
                            <span className="sr-only">{t('Open menu')}</span>
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>{t('Actions')}</DropdownMenuLabel>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem onClick={() => navigate(`/users/${user.id}`)}>
                            <Eye className="mr-2 h-4 w-4" />
                            {t('View Details')}
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => navigate(`/users/${user.id}/edit`)}>
                            <Edit className="mr-2 h-4 w-4" />
                            {t('Edit')}
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => navigate(`/users/${user.id}/reset-password`)}>
                            <Key className="mr-2 h-4 w-4" />
                            {t('Reset Password')}
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem 
                            onClick={() => user.active ? navigate(`/users/${user.id}/lock`) : navigate(`/users/${user.id}/unlock`)}
                          >
                            <Lock className="mr-2 h-4 w-4" />
                            {user.active ? t('Lock Account') : t('Unlock Account')}
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            className="text-red-600 focus:text-red-600" 
                            onClick={() => setUserToDelete(user)}
                          >
                            <Trash className="mr-2 h-4 w-4" />
                            {t('Delete')}
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
      
      <AlertDialog open={!!userToDelete} onOpenChange={(open) => !open && setUserToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{t('Delete User')}</AlertDialogTitle>
            <AlertDialogDescription>
              {t('Are you sure you want to delete this user? This action cannot be undone.')}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t('Cancel')}</AlertDialogCancel>
            <AlertDialogAction 
              onClick={handleDeleteUser}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              {deleteMutation.isPending ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Trash className="mr-2 h-4 w-4" />
              )}
              {t('Delete')}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default UserList;
