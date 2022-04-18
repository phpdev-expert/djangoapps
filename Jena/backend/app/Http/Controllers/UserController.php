<?php
namespace App\Http\Controllers;
use Illuminate\Http\Request;
use Auth;
use App\User;
use Hash;

class UserController extends Controller
{
    /**
     * Create a new controller instance.
     *
     * @return void
     */
    public function __construct()
    {
        $this->middleware('auth');
    }

    /**
     * Show the application dashboard.
     *
     * @return \Illuminate\Contracts\Support\Renderable
     */
    public function index()
    {
        $currentUser = Auth::user();
        if($currentUser->is_admin === 1) {
            $user = User::all();
        } else {
            $user = User::find($currentUser->id);
        }

        return view('users/userlist')->with('users', $user);
    }

    /**
     * Store a newly created resource in storage.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function store(Request $request)
    {
        try {
            $user = new User();
            $user->name = $request->name;
            $user->email = $request->email;
            $user->password = Hash::make($request->password);
            $user->email_verified_at = date('Y-m-d h:i:s');
            $user->created_at = date('Y-m-d h:i:s');
            $user->updated_at = date('Y-m-d h:i:s');
            $user->is_admin = $request->role;
            $user->active = $request->active;
            $isSaved = $user->save();
            if($isSaved) {
                return redirect()->route('user.list')->with('success', 'User successfully added.');
            }
        } catch(\Exception $e){
            return redirect()->route('user.list')->with('error', $e->getMessage());
        }
    }

    /**
     * Update the specified resource in storage.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  int  $id
     * @return \Illuminate\Http\Response
     */
    public function update(Request $request)
    {
        try {
            $user = User::find($request->id);
            $user->name = $request->name;
            $user->email = $request->email;
            $user->password = Hash::make($request->password);
            $user->updated_at = date('Y-m-d h:i:s');
            $user->is_admin = $request->role;
            $user->active = $request->active;
            $isSaved = $user->save();
            if($isSaved) {
                return redirect()->route('user.list')->with('success', 'User successfully updated.');
            }
        } catch(\Exception $e){
            return redirect()->route('user.list')->with('error', $e->getMessage());
        }
    }

    /**
     * Remove the specified resource from storage.
     *
     * @param  int  $id
     * @return \Illuminate\Http\Response
     */
    public function destroy(Request $request)
    {
        try {
            $user = User::find($request->id);
            $isDeleted = $user->delete();
            if($isDeleted) {
                return redirect()->route('user.list')->with('success', 'User successfully deleted.');
            }
        } catch(\Exception $e){
            return redirect()->route('user.list')->with('error', $e->getMessage());
        }
    }
}
