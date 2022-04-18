@extends('layouts.app')

@section('content')
<div class="container">
    <div class="row">
        <div class="col-md-12">
            <div class="card-error-msg">
                @include('inc/messages')
            </div>
        </div>
        <div class="col-md-12">
            <div class="card">
                <!-- <div class="card-header">Dashboard</div> -->
                <div class="card-body">
                    <div class="cus-btn-add">
                        <button
                            type="button"
                            class="btn btn-primary"
                            id="_openUserModal"
                        >Add New</button>
                    </div>

                    <table class="table table-striped">
                        <thead>
                            <tr>
                            <th scope="col">#</th>
                            <th scope="col">Name</th>
                            <th scope="col">Email</th>
                            <th scope="col">Role</th>
                            <th scope="col">Created At</th>
                            <th scope="col">Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach($users as $i=>$user): ?>
                                <tr>
                                    <th scope="row">{{ ($i+1) }}</th>
                                    <td>{{$user->name}}</td>
                                    <td>{{$user->email}}</td>
                                    <td>
                                        <span class="badge badge-info cus-user-badges">
                                            {{ ($user->is_admin == 1) ? 'Admin' : 'User' }}
                                        </span>
                                    </td>
                                    <td>{{$user->created_at}}</td>
                                    <td>
                                        <input type="hidden" class="item_value" value="{{ json_encode($user)}}">
                                        <a
                                            href="javascript:void(0)"
                                            class="_item_edit"><i class="fa fa-edit"></i> Edit</a> &nbsp;
                                        <a
                                            href="javascript:void(0)"
                                            class="_item_delete"
                                            data-id="{{$user->id}}"><i class="fa fa-delete"></i> Delete</a>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

@include('users/userform')

@include('layouts/delete')

@endsection
