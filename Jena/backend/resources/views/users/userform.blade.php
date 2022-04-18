<!-- Button trigger modal -->
<!-- <button type="button" class="btn btn-primary" data-toggle="modal" data-target="#exampleModal">
  Launch demo modal
</button> -->

<!-- Modal -->
<div
class="modal fade"
id="userModal"
tabindex="-1"
role="dialog"
aria-labelledby="exampleModalLabel"
aria-hidden="true"
backdrop="true"
>

  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="userModalLabel">Modal title</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        <form
            id="userForm"
            class="needs-validation"
            novalidate
            method="POST"
            action="{{ route('user.create') }}"
            >
            {{ csrf_field() }}
            <input type="hidden" name="id" id="user_id" value="">
            <div class="form-group">
                <label for="_inputName">Name</label>
                <input
                    id="_inputName"
                    type="text"
                    name="name"
                    class="form-control"
                    placeholder="Please enter name"
                    required
                >
                <div class="invalid-feedback">
                   Name fields is required
                </div>
            </div>
            <div class="form-group">
                <label for="_inputEmail">Email</label>
                <input
                    id="_inputEmail"
                    type="email"
                    name="email"
                    class="form-control"
                    aria-describedby="emailHelp"
                    placeholder="Enter email"
                    required
                >
                <small id="emailHelp" class="form-text text-muted">We'll never share your email with anyone else.</small>
                <div class="invalid-feedback">
                   Email fields is required
                </div>
            </div>
            <div class="form-group">
                <label for="_inputPassword">Password</label>
                <input
                    id="_inputPassword"
                    type="password"
                    class="form-control"
                    name="password"
                    placeholder="Password"
                    aria-describedby="passwordHelp"
                    required
                >
                <small id="passwordHelp" class="form-text text-muted">Please use char, number and special chars</small>
                <div class="invalid-feedback">
                   Name fields is required
                </div>
            </div>
            <div class="form-group">
                <label for="_inputRole">Role</label>
                <select
                    class="form-control"
                    id="_inputRole"
                    name="role"
                    required
                >
                    <option value="">--Select--</option>
                    <option value="1">Admin</option>
                    <option value="2">User</option>
                </select>
                <div class="invalid-feedback">
                   Role fields is required
                </div>
            </div>

            <div class="form-group">
                <label for="_inputRole">Active</label>
                <select
                    class="form-control"
                    id="_inputactive"
                    name="active"
                    required
                >
                    <option value="">--Select--</option>
                    <option value="1">Active</option>
                    <option value="0">Inactive</option>
                </select>
                <div class="invalid-feedback">
                   active fields is required
                </div>
            </div>

            <div class="modal-footer">
                <!-- <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button> -->
                <button type="submit" class="btn btn-primary">Submit</button>
            </div>
        </form>
      </div>
    </div>
  </div>
</div>
