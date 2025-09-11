/*
 * Copyright (c) by CryptoLab inc.
 * This program is licensed under a
 * Creative Commons Attribution-NonCommercial 3.0 Unported License.
 * You should have received a copy of the license along with this
 * work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.
 */

#include "../src/HEAAN.h"

using namespace std;
using namespace NTL;


int main() {
    TestScheme::testRotateByPo2Batch(13, 65, 30, 2, 5, true);
    return 0;
}
